from app.services.agents.specialist import SpecialistAgent
class CybersecurityAgent(SpecialistAgent):
 name='cybersecurity'; display_name_ar='الأمن السيبراني'; description='الأمن السيبراني'; dependencies=('evidence',); instructions='حدد المجالات الأمنية وسيناريوهات التهديد وأسئلة الضوابط والأدلة المطلوبة. لا تخترع ثغرات.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'security_domains': [], 'threats': [], 'control_questions': []},"confidence":0.0,"warnings":[],"sources":[]}
