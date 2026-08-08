from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
H={'X-Qarar-API-Key':'key-a'}

def test_create_analyze_roundtrip():
    r=client.post('/api/cases',headers=H,json={'title':'AWS decision','description':'AWS cloud data security residency decision','urgency':'high','category':'technology'})
    assert r.status_code==201
    case=r.json();assert case['tenant_id']=='tenant-a'
    a=client.post(f"/api/cases/{case['id']}/analyze",headers=H)
    assert a.status_code==200
    data=a.json();assert data['analysis_source']=='mock';assert 'cloud' in data['selected_agents'];assert 'cybersecurity' in data['selected_agents'];assert data['analysis']['executive']['human_decision_required'] is True;assert len(data['analysis']['options'])==3

def test_live_stream_emits_plan_agents_and_complete():
    r=client.post('/api/cases',headers=H,json={'title':'Project delay','description':'project blocker delay with network dependency','urgency':'high','category':'technology'})
    case=r.json();seen=[]
    with client.stream('POST',f"/api/cases/{case['id']}/analyze-stream",headers=H) as resp:
        assert resp.status_code==200
        import json
        for line in resp.iter_lines():
            if line:seen.append(json.loads(line))
    kinds=[x['type'] for x in seen];assert kinds[0]=='plan';assert 'agent_start' in kinds;assert 'agent_done' in kinds;assert kinds[-1]=='complete';plan=seen[0];assert 'project_management' in plan['selected_agents'];assert 'hr' in plan['skipped_agents'];done=[x for x in seen if x['type']=='agent_done'];assert all('estimated_cost_usd' in x for x in done)
