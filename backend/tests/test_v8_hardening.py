import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
from app.core.auth import authenticate_key
from app.core.config import settings
from app.core.database import SessionLocal
from app.main import app
from app.models.fabric import AutomationRun
from app.services.object_storage import LocalObjectStorage

client = TestClient(app)

def _signed_headers(secret: str, body: bytes, nonce: str):
    timestamp = str(int(time.time()))
    signature = hmac.new(secret.encode(), timestamp.encode()+b'.'+nonce.encode()+b'.'+body, hashlib.sha256).hexdigest()
    return {'X-Qarar-Timestamp':timestamp,'X-Qarar-Nonce':nonce,'X-Qarar-Signature':signature,'Content-Type':'application/json'}

def test_dedicated_mcp_key_is_not_admin(monkeypatch):
    monkeypatch.setattr(settings,'mcp_api_key','mcp-v8-key')
    principal=authenticate_key('mcp-v8-key')
    assert principal is not None
    assert principal.roles == ('integration_service',)
    assert 'admin' not in principal.roles

def test_local_storage_rejects_path_traversal(tmp_path):
    store=LocalObjectStorage()
    store.root=tmp_path
    try:
        store.get('../outside.txt')
    except ValueError:
        pass
    else:
        raise AssertionError('path traversal was accepted')

def test_signed_callback_accepts_once_and_rejects_replay(monkeypatch):
    secret='v8-test-secret'
    monkeypatch.setattr(settings,'automation_callback_secret',secret)
    with SessionLocal() as db:
        run=AutomationRun(tenant_id='tenant-a',actor='tester',workflow_id='decision_to_action',status='sent',approved=1,dry_run=0)
        db.add(run);db.commit();db.refresh(run);run_id=run.id
    body=json.dumps({'status':'executed','detail':{'task_id':'T-8'}},separators=(',',':')).encode()
    headers=_signed_headers(secret,body,f'nonce-{run_id}')
    first=client.post(f'/api/connect/automation/callback/{run_id}',content=body,headers=headers)
    assert first.status_code == 200
    assert first.json()['status'] == 'executed'
    replay=client.post(f'/api/connect/automation/callback/{run_id}',content=body,headers=headers)
    assert replay.status_code == 401

def test_unsigned_callback_is_rejected(monkeypatch):
    monkeypatch.setattr(settings,'automation_callback_secret','v8-test-secret')
    response=client.post('/api/connect/automation/callback/999999',json={'status':'failed','detail':{}})
    assert response.status_code == 401

def test_uploaded_fabric_evidence_reaches_decision_council():
    headers={'X-Qarar-API-Key':'key-a'}
    created=client.post('/api/cases',headers=headers,json={
        'title':'V8 evidence integration','description':'Choose an implementation plan using the approved budget evidence.',
        'urgency':'high','category':'finance','language':'en'})
    assert created.status_code == 201
    case_id=created.json()['id']
    uploaded=client.post('/api/fabric/upload',headers=headers,data={'case_id':str(case_id),'trust_level':'B'},
                         files={'file':('approved-budget.txt',b'Approved program budget is SAR 500,000.','text/plain')})
    assert uploaded.status_code == 200
    analyzed=client.post(f'/api/cases/{case_id}/analyze',headers=headers)
    assert analyzed.status_code == 200
    analysis=analyzed.json()['analysis']
    assert any('500,000' in fact for fact in analysis['facts'])
    assert analysis['evidence_sources'][0]['title']=='approved-budget.txt'
