from app.services.agents.specialist import SpecialistAgent
class EvidenceAgent(SpecialistAgent):
 name='evidence'; display_name_ar='الأدلة والمعلومات'; description='الأدلة والمعلومات'; dependencies=(); instructions='افصل بين الحقائق المذكورة والادعاءات والافتراضات والمعلومات الناقصة والأدلة المطلوبة. لا تعط توصية ولا تخترع مصادر.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'facts': [], 'claims': [], 'assumptions': [], 'missing_information': [], 'required_evidence': [], 'readiness': 'low|medium|high'},"confidence":0.0,"warnings":[],"sources":[]}
