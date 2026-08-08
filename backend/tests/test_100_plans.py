from app.services.contracts import CaseInput
from app.services.planner import build_plan
from app.services.registry import SPECIALISTS
samples=['AWS cloud security data residency','vendor contract SLA procurement','project status blocker delay milestone','budget cost ROI finance','HR employee training skills','DR BCP RTO RPO operations','strategy stakeholder owner','architecture integration target state','simple management priority','NCA compliance cybersecurity data classification']
def test_100_planner_runs():
 for i in range(100):
  p=build_plan(CaseInput(i,samples[i%len(samples)],samples[i%len(samples)],'high','general'),SPECIALISTS)
  assert p.selected[0]=='evidence';assert 'risk' in p.selected;assert not(set(p.selected)&set(p.skipped));assert set(p.selected)|set(p.skipped)==set(SPECIALISTS)
