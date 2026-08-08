from app.services.agents.specialist import SpecialistAgent
class OperationsAgent(SpecialistAgent):
 name='operations'; display_name_ar='التشغيل والدعم'; description='التشغيل والدعم'; dependencies=('evidence',); instructions='حدد المراقبة والدعم وRunbook والملكية والتصعيد والأتمتة.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'support_gaps': [], 'monitoring_needs': [], 'runbook_needs': []},"confidence":0.0,"warnings":[],"sources":[]}
