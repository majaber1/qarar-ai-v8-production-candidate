from __future__ import annotations
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from fastapi import APIRouter,BackgroundTasks,Depends,File,Form,HTTPException,Response,UploadFile
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.audit import record_audit
from app.core.auth import Principal, require_principal
from app.core.config import settings
from app.core.database import get_db
from app.core.ratelimit import check_ai_rate_limit, check_budget
from app.models.fabric import KnowledgeSource
from app.models.case import DecisionCase
from app.models.workspace import Project
from app.services.object_storage import storage
from app.services.fabric import ingest_source,hybrid_search
from app.services.knowledge_qa import ask_knowledge
from app.services.research import research_status,web_research

router=APIRouter(prefix='/fabric',tags=['knowledge-fabric'])
ALLOWED_EVIDENCE_TYPES={
    'application/json','application/pdf','application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/csv','text/markdown','text/plain',
}

class Ask(BaseModel):
    question:str=Field(min_length=3)
    case_id:int|None=None
    language:str='ar'
    mode:str|None=None

class Research(BaseModel):
    query:str=Field(min_length=3)
    mode:str='official_plus_organization'

class EvidenceUpdate(BaseModel):
    title:str|None=Field(default=None,min_length=2,max_length=500)
    source_ref:str|None=Field(default=None,max_length=1500)
    source_owner:str|None=Field(default=None,max_length=200)
    trust_level:str|None=None
    reviewed:bool=False

@router.post('/upload')
async def upload(
    background:BackgroundTasks,
    file:UploadFile=File(...),
    case_id:int|None=Form(None),
    project_id:int|None=Form(None),
    trust_level:str=Form('B'),
    source_type:str=Form('file'),
    supersedes_id:int|None=Form(None),
    db:Session=Depends(get_db),
    principal:Principal=Depends(require_principal),
):
    data=await file.read(); maxb=settings.max_file_mb*1024*1024
    if not data: raise HTTPException(422,'Evidence file must not be empty')
    if len(data)>maxb: raise HTTPException(413,f'File too large; max {settings.max_file_mb} MB')
    content_type=(file.content_type or '').lower().split(';',1)[0]
    if content_type not in ALLOWED_EVIDENCE_TYPES: raise HTTPException(415,'Unsupported evidence file type')
    if case_id is not None and not db.scalar(select(DecisionCase).where(DecisionCase.id==case_id,DecisionCase.tenant_id==principal.tenant_id)):
        raise HTTPException(404,'Case not found')
    if project_id is not None and not db.scalar(select(Project).where(Project.id==project_id,Project.tenant_id==principal.tenant_id)):
        raise HTTPException(404,'Project not found')
    previous=None
    if supersedes_id is not None:
        previous=db.scalar(select(KnowledgeSource).where(KnowledgeSource.id==supersedes_id,KnowledgeSource.tenant_id==principal.tenant_id,KnowledgeSource.deleted_at.is_(None)))
        if not previous:raise HTTPException(404,'Evidence version to replace not found')
        case_id=case_id if case_id is not None else previous.case_id;project_id=project_id if project_id is not None else previous.project_id
    try:key=storage().put(file.filename or 'upload.bin',data)
    except Exception as e: raise HTTPException(500,f'Object storage failed: {e}')
    # Trust A is reserved for verified/curated sources; ordinary upload cannot self-assert A.
    effective_trust = trust_level if trust_level in {'B','C','D'} else 'B'
    src=KnowledgeSource(
        tenant_id=principal.tenant_id,case_id=case_id,project_id=project_id,source_type=source_type,title=file.filename or 'Uploaded file',
        source_ref=file.filename,object_key=key,trust_level=effective_trust,status='queued',
        metadata_json=json.dumps({'content_type':content_type,'size_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'uploaded_by':principal.subject}),source_owner=principal.subject,
        version=(previous.version+1 if previous else 1),supersedes_id=(previous.id if previous else None)
    )
    db.add(src)
    if previous:previous.status='superseded';previous.deleted_at=datetime.now(timezone.utc)
    db.commit();db.refresh(src)
    if settings.ingestion_mode=='background': background.add_task(ingest_source,src.id)
    else: ingest_source(src.id);db.refresh(src)
    record_audit(principal.tenant_id,principal.subject,'evidence_uploaded',auth_type=principal.auth_type,
                 resource_type='knowledge_source',resource_id=src.id,
                 metadata={'title':src.title,'status':src.status,'trust_level':src.trust_level,'version':src.version,'supersedes_id':src.supersedes_id,'malware_scan_enabled':settings.malware_scan_enabled})
    return {'id':src.id,'title':src.title,'status':src.status,'trust_level':src.trust_level,'size_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
            'object_key':src.object_key,'version':src.version,'supersedes_id':src.supersedes_id,'error':src.error,'malware_scan_enabled':settings.malware_scan_enabled}

@router.get('/sources')
def sources(case_id:int|None=None,project_id:int|None=None,db:Session=Depends(get_db),principal:Principal=Depends(require_principal)):
    q=select(KnowledgeSource).where(KnowledgeSource.tenant_id==principal.tenant_id,KnowledgeSource.deleted_at.is_(None)).order_by(KnowledgeSource.created_at.desc())
    if case_id is not None:q=q.where((KnowledgeSource.case_id==case_id)|(KnowledgeSource.case_id.is_(None)))
    if project_id is not None:q=q.where(KnowledgeSource.project_id==project_id)
    return [{'id':x.id,'case_id':x.case_id,'project_id':x.project_id,'source_type':x.source_type,'title':x.title,'source_ref':x.source_ref,'source_owner':x.source_owner,'trust_level':x.trust_level,'status':x.status,'version':x.version,'reviewed_at':x.reviewed_at,'supersedes_id':x.supersedes_id,'error':x.error,'created_at':x.created_at} for x in db.scalars(q).all()]

@router.get('/sources/{source_id}/download')
def download_source(source_id:int,db:Session=Depends(get_db),principal:Principal=Depends(require_principal)):
    source=db.scalar(select(KnowledgeSource).where(KnowledgeSource.id==source_id,KnowledgeSource.tenant_id==principal.tenant_id,KnowledgeSource.deleted_at.is_(None)))
    if not source or not source.object_key:raise HTTPException(404,'Evidence object not found')
    try:data=storage().get(source.object_key)
    except FileNotFoundError:raise HTTPException(404,'Evidence object not found')
    except Exception as exc:raise HTTPException(502,f'Object storage read failed: {exc}')
    metadata=json.loads(source.metadata_json or '{}')
    filename=Path(source.source_ref or source.title or 'evidence.bin').name.replace('"','_')
    return Response(content=data,media_type=metadata.get('content_type') or 'application/octet-stream',headers={'Content-Disposition':f'attachment; filename="{filename}"','X-Content-SHA256':metadata.get('sha256','')})

@router.patch('/sources/{source_id}')
def update_source(source_id:int,req:EvidenceUpdate,db:Session=Depends(get_db),principal:Principal=Depends(require_principal)):
    source=db.scalar(select(KnowledgeSource).where(KnowledgeSource.id==source_id,KnowledgeSource.tenant_id==principal.tenant_id,KnowledgeSource.deleted_at.is_(None)))
    if not source:raise HTTPException(404,'Evidence not found')
    values=req.model_dump(exclude_unset=True);reviewed=values.pop('reviewed',False)
    if values.get('trust_level') not in {None,'B','C','D'}:raise HTTPException(422,'Trust level must be B, C, or D')
    for key,value in values.items():setattr(source,key,value)
    if reviewed:source.reviewed_at=datetime.now(timezone.utc)
    db.commit();db.refresh(source)
    record_audit(principal.tenant_id,principal.subject,'evidence_updated',auth_type=principal.auth_type,resource_type='knowledge_source',resource_id=source.id,metadata={'fields':sorted(values),'reviewed':reviewed})
    return {'id':source.id,'title':source.title,'version':source.version,'trust_level':source.trust_level,'reviewed_at':source.reviewed_at}

@router.delete('/sources/{source_id}')
def delete_source(source_id:int,db:Session=Depends(get_db),principal:Principal=Depends(require_principal)):
    source=db.scalar(select(KnowledgeSource).where(KnowledgeSource.id==source_id,KnowledgeSource.tenant_id==principal.tenant_id,KnowledgeSource.deleted_at.is_(None)))
    if not source:raise HTTPException(404,'Evidence not found')
    source.deleted_at=datetime.now(timezone.utc);source.status='deleted';db.commit()
    if source.object_key:
        try:storage().delete(source.object_key)
        except Exception as exc:raise HTTPException(502,f'Evidence metadata deleted but object removal failed: {exc}')
    record_audit(principal.tenant_id,principal.subject,'evidence_deleted',auth_type=principal.auth_type,resource_type='knowledge_source',resource_id=source.id)
    return {'status':'deleted','id':source.id}

@router.get('/search')
def search(q:str,case_id:int|None=None,limit:int=10,principal:Principal=Depends(require_principal)):
    return {'query':q,'results':hybrid_search(q,case_id=case_id,tenant_id=principal.tenant_id,limit=min(max(limit,1),30))}

@router.post('/ask')
def ask(req:Ask,principal:Principal=Depends(require_principal)):
    ok,reason=check_budget(principal.tenant_id)
    if not ok:raise HTTPException(429,reason)
    ok,reason=check_ai_rate_limit(principal.subject)
    if not ok:raise HTTPException(429,reason)
    return ask_knowledge(req.question,req.case_id,req.language,req.mode,tenant_id=principal.tenant_id)

@router.get('/research/status')
def status(principal:Principal=Depends(require_principal)):
    return research_status()

@router.post('/research')
def research(req:Research,principal:Principal=Depends(require_principal)):
    return web_research(req.query,req.mode)
