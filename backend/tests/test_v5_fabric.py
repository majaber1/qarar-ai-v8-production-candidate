from app.services.fabric import chunk_text,lexical
from app.services.automation import execute
from app.services.research import research_status

def test_chunking_large_text():
    x=chunk_text(('cloud data policy security '*400),size=500,overlap=50)
    assert len(x)>5 and all(len(c)<=520 for c in x)
def test_lexical():assert lexical('cloud security','cloud migration security controls')>0
def test_automation_defaults_to_dry_run():
    # No case_id: dry-run with a case-less payload is allowed (e.g. a generic workflow probe).
    # V6 validates case_id tenant ownership even on dry runs (see test_security_v51.py for the
    # case-scoped variant), so this test intentionally omits case_id rather than referencing a
    # case_id that doesn't exist for tenant 'test'.
    r=execute('decision_to_action',{},dry_run=True,tenant_id='test',actor='tester');assert r['status']=='dry_run'
def test_research_modes_present():assert 'official_plus_organization' in research_status()['modes']
