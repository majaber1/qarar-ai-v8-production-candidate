from app.services.agents.specialist import SpecialistAgent
class ComplianceAgent(SpecialistAgent):
 name='compliance'; display_name_ar='الالتزام'; description='الالتزام'; dependencies=('evidence',); instructions='حدد الأطر أو مجالات الالتزام والأدلة المطلوبة والفجوات المحتملة. لا تدّع الامتثال بدون دليل.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'frameworks_to_verify': [], 'evidence_needed': [], 'potential_gaps': []},"confidence":0.0,"warnings":[],"sources":[]}
