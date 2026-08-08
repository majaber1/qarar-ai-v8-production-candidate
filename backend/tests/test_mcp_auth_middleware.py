from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.core.auth import current_principal
from app.core.mcp_auth import MCPAuthMiddleware

inner=FastAPI()
@inner.get('/mcp')
def protected():
    p=current_principal();return {'tenant_id':p.tenant_id,'subject':p.subject}
app=MCPAuthMiddleware(inner)
client=TestClient(app)

def test_mcp_anonymous_rejected():
    assert client.get('/mcp').status_code==401

def test_mcp_authenticated_allowed_and_context_set():
    r=client.get('/mcp',headers={'Authorization':'Bearer key-a'})
    assert r.status_code==200
    assert r.json()['tenant_id']=='tenant-a'
