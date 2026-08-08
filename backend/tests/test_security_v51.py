import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.automation import execute

client=TestClient(app)
HA={'X-Qarar-API-Key':'key-a'}
HB={'X-Qarar-API-Key':'key-b'}
READER={'X-Qarar-API-Key':'reader-a'}

def create(headers,title='Tenant case'):
    return client.post('/api/cases',headers=headers,json={'title':title,'description':'A sufficiently detailed decision case description','urgency':'high','category':'general'})

def test_unauthenticated_api_is_rejected():
    assert client.get('/api/cases').status_code==401
    assert client.get('/api/platform/catalog').status_code==401
    assert client.get('/api/connect/catalog').status_code==401

def test_whoami():
    r=client.get('/api/whoami',headers=HA);assert r.status_code==200;assert r.json()['tenant_id']=='tenant-a'

def test_tenant_case_isolation():
    a=create(HA,'A-only').json();b=create(HB,'B-only').json()
    assert client.get(f"/api/cases/{a['id']}",headers=HB).status_code==404
    assert client.get(f"/api/cases/{b['id']}",headers=HA).status_code==404
    assert all(x['tenant_id']=='tenant-a' for x in client.get('/api/cases',headers=HA).json())

def test_role_gate_blocks_analysis_for_read_only_role():
    c=create(HA,'Role case').json()
    assert client.post(f"/api/cases/{c['id']}/analyze",headers=READER).status_code==403

def test_non_dry_automation_requires_server_verified_approval(monkeypatch):
    c=create(HA,'Approval case').json()
    monkeypatch.setattr(settings,'automation_enabled',True)
    monkeypatch.setattr(settings,'automation_require_approval',True)
    with pytest.raises(PermissionError):
        execute('decision_to_action',{'case_id':c['id']},dry_run=False,tenant_id='tenant-a',actor='admin-a')

def test_client_supplied_approved_flag_no_longer_exists():
    r=client.post('/api/connect/automation/run',headers=HA,json={'workflow_id':'decision_to_action','case_id':999,'payload':{},'approved':True,'dry_run':False})
    # Pydantic ignores unknown approved, and server verification still blocks execution.
    assert r.status_code in {400,403}

def test_fabric_is_tenant_scoped_and_upload_cannot_self_assert_trust_a():
    files={'file':('policy.txt',b'cloud security policy', 'text/plain')}
    r=client.post('/api/fabric/upload',headers=HA,files=files,data={'trust_level':'A'})
    assert r.status_code==200
    assert r.json()['trust_level']=='B'
    src_id=r.json()['id']
    a_sources=client.get('/api/fabric/sources',headers=HA).json()
    b_sources=client.get('/api/fabric/sources',headers=HB).json()
    assert any(x['id']==src_id for x in a_sources)
    assert all(x['id']!=src_id for x in b_sources)


def test_approval_record_allows_execution_gate_then_n8n_is_attempted(monkeypatch):
    c=create(HA,'Approved execution').json()
    analyzed=client.post(f"/api/cases/{c['id']}/analyze",headers=HA).json()
    option=analyzed['analysis']['options'][0]['id']
    approved=client.post(f"/api/cases/{c['id']}/approve",headers=HA,json={'option_id':option,'decision_owner':'Owner A'})
    assert approved.status_code==200 and approved.json()['status']=='approved'
    monkeypatch.setattr(settings,'automation_enabled',True)
    monkeypatch.setattr(settings,'automation_require_approval',True)
    class FakeResponse:
        status_code=200;text='ok'
        def raise_for_status(self):return None
    import app.services.automation as auto
    monkeypatch.setattr(auto.httpx,'post',lambda *a,**k:FakeResponse())
    r=execute('decision_to_action',{'case_id':c['id']},dry_run=False,tenant_id='tenant-a',actor='admin-a')
    assert r['status']=='sent'
