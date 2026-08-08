from app.services.agents.specialist import SpecialistAgent
class CloudAgent(SpecialistAgent):
 name='cloud'; display_name_ar='السحابة والبنية التحتية'; description='السحابة والبنية التحتية'; dependencies=('evidence',); instructions='حدد أسئلة المنطقة والإقامة والاتصال والتوافر والنسخ الاحتياطي. لا تدّع إعدادات غير مقدمة.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'cloud_questions': [], 'residency_questions': [], 'connectivity_questions': []},"confidence":0.0,"warnings":[],"sources":[]}
