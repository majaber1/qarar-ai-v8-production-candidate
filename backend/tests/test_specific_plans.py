from app.services.contracts import CaseInput
from app.services.planner import build_plan
from app.services.registry import SPECIALISTS
def p(t):return build_plan(CaseInput(None,t,t,'high','general'),SPECIALISTS)
def test_simple_skips_cloud():assert 'cloud' in p('simple management priority').skipped
def test_cloud_selects_cloud_data_cyber():
 x=p('AWS cloud security data residency');assert {'cloud','cybersecurity','data_governance'}<=set(x.selected)
def test_vendor_selects_legal_procurement():
 x=p('vendor contract SLA procurement');assert {'legal','procurement'}<=set(x.selected)
