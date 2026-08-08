from app.services.contracts import CaseInput
from app.services.orchestrator import orchestrator

def analyze_case(case_id, title, description, urgency, category=None, language='ar', tenant_id='default'):
    return orchestrator.analyze(CaseInput(case_id, title, description, urgency, category, language, tenant_id))
