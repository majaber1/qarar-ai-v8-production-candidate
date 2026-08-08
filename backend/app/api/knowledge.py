import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.auth import Principal, require_principal
from app.core.database import get_db
from app.models.knowledge import KnowledgeItem
from app.services.knowledge import extract_text, top_context
from app.services.email_connector import sync_imap
from app.services.llm_client import LLMClient
from app.core.config import settings

router = APIRouter(prefix='/knowledge', tags=['knowledge-compat'])

class AskRequest(BaseModel):
    question: str = Field(min_length=3)
    case_id: int | None = None
    language: str = 'ar'

@router.post('/upload')
async def upload(file: UploadFile = File(...), case_id: int | None = Form(None), db: Session = Depends(get_db), principal:Principal=Depends(require_principal)):
    data = await file.read()
    if len(data) > settings.max_file_mb * 1024 * 1024:
        raise HTTPException(413, f'File too large; max {settings.max_file_mb} MB')
    try:text = extract_text(file.filename or 'upload.txt', data)
    except Exception as e:raise HTTPException(400, str(e))
    if not text.strip():raise HTTPException(400, 'No readable text extracted')
    item = KnowledgeItem(tenant_id=principal.tenant_id,case_id=case_id,source_type='file',title=file.filename or 'Uploaded file',source_ref=file.filename,content=text,metadata_json=json.dumps({'content_type': file.content_type, 'size_bytes': len(data),'uploaded_by':principal.subject}))
    db.add(item); db.commit(); db.refresh(item)
    return {'id': item.id, 'title': item.title, 'characters': len(text), 'source_type': 'file'}

@router.get('/items')
def items(case_id: int | None = None, db: Session = Depends(get_db),principal:Principal=Depends(require_principal)):
    q = select(KnowledgeItem).where(KnowledgeItem.tenant_id==principal.tenant_id).order_by(KnowledgeItem.created_at.desc())
    if case_id is not None:q = q.where(KnowledgeItem.case_id == case_id)
    xs = list(db.scalars(q).all())
    return [{'id': x.id, 'case_id': x.case_id, 'source_type': x.source_type, 'title': x.title,'source_ref': x.source_ref, 'created_at': x.created_at} for x in xs]

@router.post('/email/sync')
def email_sync(case_id: int | None = None, limit: int = 25, db: Session = Depends(get_db),principal:Principal=Depends(require_principal)):
    try:messages = sync_imap(min(max(limit, 1), 100))
    except Exception as e:raise HTTPException(400, str(e))
    added = 0
    for m in messages:
        ref = 'imap:' + m['message_id']
        existing = db.scalar(select(KnowledgeItem).where(KnowledgeItem.tenant_id==principal.tenant_id,KnowledgeItem.source_ref == ref))
        if existing:continue
        content = f"From: {m['from']}\nDate: {m['date']}\nSubject: {m['subject']}\n\n{m['body']}"
        db.add(KnowledgeItem(tenant_id=principal.tenant_id,case_id=case_id,source_type='email',title=m['subject'] or '(no subject)',source_ref=ref,content=content,metadata_json=json.dumps({'from': m['from'], 'date': m['date']})))
        added += 1
    db.commit(); return {'synced': len(messages), 'added': added}

@router.get('/email/status')
def email_status(principal:Principal=Depends(require_principal)):
    return {'imap': {'configured': bool(settings.imap_enabled and settings.imap_host and settings.imap_username and settings.imap_password),'provider': 'Generic IMAP'},'microsoft365': {'configured': bool(settings.m365_client_id and settings.m365_tenant_id),'mode': 'oauth_scaffold'},'gmail': {'configured': bool(settings.google_client_id),'mode': 'oauth_scaffold'}}

@router.post('/ask')
def ask(req: AskRequest, db: Session = Depends(get_db),principal:Principal=Depends(require_principal)):
    q = select(KnowledgeItem).where(KnowledgeItem.tenant_id==principal.tenant_id).order_by(KnowledgeItem.created_at.desc())
    if req.case_id is not None:q = q.where((KnowledgeItem.case_id == req.case_id) | (KnowledgeItem.case_id.is_(None)))
    xs = list(db.scalars(q).all())
    if not xs:raise HTTPException(400, 'No files or emails are available yet')
    chunks = top_context(req.question, xs)
    context = '\n\n'.join(f"[SOURCE {c['id']}: {c['title']} / {c['source_type']}]\n{c['text']}" for c in chunks)
    if settings.ai_enabled and settings.ai_provider == 'openai' and settings.ai_api_key:
        lang = 'Arabic' if req.language == 'ar' else 'English'
        prompt = f"Answer in {lang}. Answer only from the supplied evidence. If the evidence does not support the answer, say that clearly. Be concise. Cite supporting source IDs like [S12]. Do not invent facts."
        answer = LLMClient().generate(prompt,f"QUESTION:\n{req.question}\n\nEVIDENCE:\n{context}")
    else:answer = 'وضع تجريبي: تم العثور على مصادر ذات صلة، لكن AI غير مفعّل.' if req.language == 'ar' else 'Demo mode: relevant sources were found, but AI is disabled.'
    return {'answer': answer,'sources': [{'id': c['id'], 'title': c['title'], 'source_type': c['source_type']} for c in chunks]}
