from fastapi.testclient import TestClient
from app.main import app
from app.services.tools.scoring import score_options,sensitivity_analysis

client=TestClient(app);A={'X-Qarar-API-Key':'key-a'};B={'X-Qarar-API-Key':'key-b'}

def _case():
    response=client.post('/api/cases',headers=A,json={'title':'Decision loop','description':'Choose a controlled implementation path with measurable outcomes.','scoring_criteria':[{'key':'cost','name':'Cost','description':'Lower cost is preferred','weight':2,'scale_min':0,'scale_max':100,'direction':'lower_better'},{'key':'value','name':'Value','description':'Higher value is preferred','weight':1}]})
    assert response.status_code==201,response.text
    return response.json()

def test_custom_scales_direction_missing_and_ties_are_transparent():
    criteria=[{'key':'cost','name':'Cost','weight':1,'scale_min':0,'scale_max':10,'direction':'lower_better'},{'key':'value','name':'Value','weight':1,'scale_min':0,'scale_max':10}]
    scored=score_options([{'id':'A','criterion_scores':{'cost':2,'value':8}},{'id':'B','criterion_scores':{'cost':2,'value':8}},{'id':'C','criterion_scores':{'cost':1}}],criteria=criteria)
    assert scored[0]['weighted_score']==80
    assert scored[0]['rank_status']=='tied'
    assert scored[-1]['weighted_score'] is None and scored[-1]['missing_criteria']==['value']
    assert scored[0]['criterion_details'][0]['normalized_score']==80

def test_sensitivity_recalculates_and_labels_instability():
    criteria=[{'key':'risk','name':'Risk','weight':.5},{'key':'value','name':'Value','weight':.5}]
    options=[{'id':'A','criterion_scores':{'risk':90,'value':40}},{'id':'B','criterion_scores':{'risk':50,'value':90}}]
    result=sensitivity_analysis(options,criteria,{'risk':.9,'value':.1})
    assert result['baseline_leader']=='B' and result['scenario_leader']=='A'
    assert result['stability']=='highly_sensitive'

def test_lifecycle_actions_outcomes_and_tenant_isolation():
    case=_case();cid=case['id'];assert case['status']=='draft'
    assert client.post(f'/api/cases/{cid}/transition',headers=A,json={'status':'ready_for_analysis','reason':'Context and evidence are ready'}).status_code==200
    assert client.post(f'/api/cases/{cid}/transition',headers=A,json={'status':'approved','reason':'Skip analysis'}).status_code==409
    action=client.post(f'/api/cases/{cid}/actions',headers=A,json={'title':'Validate contract','owner':'Owner A','priority':'high'});assert action.status_code==201,action.text
    aid=action.json()['id'];assert client.get(f'/api/cases/{cid}/actions',headers=B).status_code==404
    completed=client.patch(f'/api/cases/{cid}/actions/{aid}',headers=A,json={'status':'completed'});assert completed.status_code==200 and completed.json()['completion_date']
    assert client.post(f'/api/cases/{cid}/outcomes',headers=A,json={'result':'success','expected_result':'Expected','actual_result':'Actual'}).status_code==409

def test_project_update_archive_and_summary():
    project=client.post('/api/projects',headers=A,json={'name':'Decision portfolio','objective':'Link cases, evidence, and outcomes safely.','owner':'PM'}).json()
    updated=client.patch(f"/api/projects/{project['id']}",headers=A,json={'status':'archived','owner':'Executive PM'})
    assert updated.status_code==200 and updated.json()['status']=='archived'
    detail=client.get(f"/api/projects/{project['id']}",headers=A).json()
    assert detail['summary']=={'cases':0,'approved_cases':0,'open_cases':0,'evidence':0}
    assert client.patch(f"/api/projects/{project['id']}",headers=B,json={'status':'active'}).status_code==404

def test_evidence_metadata_replacement_and_soft_delete_exclude_old_versions():
    first=client.post('/api/fabric/upload',headers=A,files={'file':('source.txt',b'approved source version one','text/plain')},data={'trust_level':'B'})
    assert first.status_code==200,first.text
    source_id=first.json()['id']
    assert len(first.json()['sha256'])==64
    downloaded=client.get(f'/api/fabric/sources/{source_id}/download',headers=A)
    assert downloaded.status_code==200 and downloaded.content==b'approved source version one'
    assert downloaded.headers['x-content-sha256']==first.json()['sha256']
    assert client.get(f'/api/fabric/sources/{source_id}/download',headers=B).status_code==404
    reviewed=client.patch(f'/api/fabric/sources/{source_id}',headers=A,json={'source_ref':'https://example.invalid/source','source_owner':'Evidence owner','reviewed':True})
    assert reviewed.status_code==200 and reviewed.json()['reviewed_at']
    replacement=client.post('/api/fabric/upload',headers=A,files={'file':('source-v2.txt',b'approved source version two','text/plain')},data={'trust_level':'B','supersedes_id':str(source_id)})
    assert replacement.status_code==200 and replacement.json()['version']==2 and replacement.json()['supersedes_id']==source_id
    listed=client.get('/api/fabric/sources',headers=A).json()
    assert source_id not in {x['id'] for x in listed}
    replacement_id=replacement.json()['id']
    assert client.delete(f'/api/fabric/sources/{replacement_id}',headers=B).status_code==404
    assert client.delete(f'/api/fabric/sources/{replacement_id}',headers=A).status_code==200
    assert replacement_id not in {x['id'] for x in client.get('/api/fabric/sources',headers=A).json()}

def test_evidence_rejects_empty_and_unsupported_files():
    empty=client.post('/api/fabric/upload',headers=A,files={'file':('empty.txt',b'','text/plain')})
    assert empty.status_code==422
    executable=client.post('/api/fabric/upload',headers=A,files={'file':('unsafe.exe',b'MZ','application/x-msdownload')})
    assert executable.status_code==415
