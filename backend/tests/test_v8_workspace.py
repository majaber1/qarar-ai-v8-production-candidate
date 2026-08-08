from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
ADMIN = {'X-Qarar-API-Key': 'key-a'}


def test_registration_requires_approval_then_password_login_works():
    registered = client.post('/api/auth/register', json={
        'full_name': 'Project Operator', 'email': 'operator@example.com', 'organization': 'Tenant A',
        'workspace_code': 'tenant-a', 'password': 'a-strong-password-123', 'requested_role': 'project_manager'})
    assert registered.status_code == 202
    pending_login = client.post('/api/auth/login', json={
        'email': 'operator@example.com', 'workspace_code': 'tenant-a', 'password': 'a-strong-password-123'})
    assert pending_login.status_code == 403
    request_id = registered.json()['id']
    approved = client.post(f'/api/access-requests/{request_id}/approve', headers=ADMIN)
    assert approved.status_code == 200
    logged_in = client.post('/api/auth/login', json={
        'email': 'operator@example.com', 'workspace_code': 'tenant-a', 'password': 'a-strong-password-123'})
    assert logged_in.status_code == 200
    token = logged_in.json()['token']
    whoami = client.get('/api/whoami', headers={'X-Qarar-API-Key': token})
    assert whoami.status_code == 200
    assert whoami.json()['roles'] == ['project_manager']
    assert client.post('/api/auth/logout', json={'token': token}).status_code == 200
    assert client.get('/api/whoami', headers={'X-Qarar-API-Key': token}).status_code == 401


def test_project_case_and_file_are_tenant_scoped_and_linked():
    project = client.post('/api/projects', headers=ADMIN, json={
        'name': 'Eastern expansion', 'objective': 'Validate the expansion business case.', 'owner': 'Strategy Office'})
    assert project.status_code == 201
    project_id = project.json()['id']
    case = client.post('/api/cases', headers=ADMIN, json={
        'project_id': project_id, 'title': 'Approve expansion',
        'description': 'Assess whether the organization should approve the expansion.',
        'urgency': 'high', 'category': 'option', 'language': 'en'})
    assert case.status_code == 201
    assert case.json()['project_id'] == project_id
    uploaded = client.post('/api/fabric/upload', headers=ADMIN,
        data={'project_id': str(project_id), 'case_id': str(case.json()['id']), 'trust_level': 'B'},
        files={'file': ('business-case.txt', b'Expected first-year revenue is SAR 12 million.', 'text/plain')})
    assert uploaded.status_code == 200
    sources = client.get(f'/api/fabric/sources?project_id={project_id}', headers=ADMIN)
    assert sources.status_code == 200
    assert sources.json()[0]['project_id'] == project_id
    foreign = client.get(f'/api/projects/{project_id}', headers={'X-Qarar-API-Key': 'key-b'})
    assert foreign.status_code == 404


def test_case_rejects_project_from_another_tenant():
    project = client.post('/api/projects', headers=ADMIN, json={
        'name': 'Tenant A project', 'objective': 'Keep tenant boundaries enforced.', 'owner': 'Security'})
    response = client.post('/api/cases', headers={'X-Qarar-API-Key': 'key-b'}, json={
        'project_id': project.json()['id'], 'title': 'Cross tenant case',
        'description': 'This request must not reference another tenant project.',
        'urgency': 'medium', 'category': 'problem', 'language': 'en'})
    assert response.status_code == 404
