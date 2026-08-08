from app.services.agents.specialist import SpecialistAgent
class BusinessContinuityAgent(SpecialistAgent):
 name='business_continuity'; display_name_ar='استمرارية الأعمال'; description='استمرارية الأعمال'; dependencies=('evidence',); instructions='حدد الحاجة إلى RTO/RPO والتعافي والتوافر والاختبارات.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'rto_rpo_questions': [], 'recovery_questions': [], 'availability_questions': []},"confidence":0.0,"warnings":[],"sources":[]}
