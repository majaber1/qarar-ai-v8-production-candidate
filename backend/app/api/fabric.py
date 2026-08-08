from __future__ import annotations
import json
from fastapi import APIRouter,BackgroundTasks,Depends,File,Form,HTTPException,UploadFile
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

class Ask(BaseModel):
    question:str=Field(min_length=3)
    case_id:int|None=None
    language:str='ar'
    mode:str|None=None

class Research(BaseModel):
    query:str=Field(min_length=3)
    mode:str='official_plus_organization'

@router.post('/upload')
async def upload(
    background:BackgroundTasks,
    file:UploadFile=File(...),
    case_id:int|None=Form(None),
    project_id:int|None=Form(None),
    trust_level:str=Form('B'),
    source_type:str=Form('file'),
    db:Session=Depends(get_db),
    principal:Principal=Depends(require_principal),
):
    data=await file.read(); maxb=settings.max_file_mb*1024*1024
    if len(data)>maxb: raise HTTPException(413,f'File too large; max {settings.max_file_mb} MB')
    if case_id is not None and not db.scalar(select(DecisionCase).where(DecisionCase.id==case_id,DecisionCase.tenant_id==principal.tenant_id)):
        raise HTTPException(404,'Case not found')
    if project_id is not None and not db.scalar(select(Project).where(Project.id==project_id,Project.tenant_id==principal.tenant_id)):
        raise HTTPException(404,'Project not found')
    try:key=storage().put(file.filename or 'upload.bin',data)
    except Exception as e: raise HTTPException(500,f'Object storage failed: {e}')
    # Trust A is reserved for verified/curated sources; ordinary upload cannot self-assert A.
    effective_trust = trust_level if trust_level in {'B','C','D'} else 'B'
    src=KnowledgeSource(
        tenant_id=principal.tenant_id,case_id=case_id,project_id=project_id,source_type=source_type,title=file.filename or 'Uploaded file',
        source_ref=file.filename,object_key=key,trust_level=effective_trust,status='queued',
        metadata_json=json.dumps({'content_type':file.content_type,'size_bytes':len(data),'uploaded_by':principal.subject})
    )
    db.add(src);db.commit();db.refresh(src)
    if settings.ingestion_mode=='background': background.add_task(ingest_source,src.id)
    else: ingest_source(src.id);db.refresh(src)
    record_audit(principal.tenant_id,principal.subject,'evidence_uploaded',auth_type=principal.auth_type,
                 resource_type='knowledge_source',resource_id=src.id,
                 metadata={'title':src.title,'status':src.status,'trust_level':src.trust_level,'malware_scan_enabled':settings.malware_scan_enabled})
    return {'id':src.id,'title':src.title,'status':src.status,'trust_level':src.trust_level,'size_bytes':len(data),
            'object_key':src.object_key,'error':src.error,'malware_scan_enabled':settings.malware_scan_enabled}

@router.get('/sources')
def sources(case_id:int|None=None,project_id:int|None=None,db:Session=Depends(get_db),principal:Principal=Depends(require_principal)):
    q=select(KnowledgeSource).where(KnowledgeSource.tenant_id==principal.tenant_id).order_by(KnowledgeSource.created_at.desc())
    if case_id is not None:q=q.where((KnowledgeSource.case_id==case_id)|(KnowledgeSource.case_id.is_(None)))
    if project_id is not None:q=q.where(KnowledgeSource.project_id==project_id)
    return [{'id':x.id,'case_id':x.case_id,'project_id':x.project_id,'source_type':x.source_type,'title':x.title,'source_ref':x.source_ref,'trust_level':x.trust_level,'status':x.status,'error':x.error,'created_at':x.created_at} for x in db.scalars(q).all()]

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
