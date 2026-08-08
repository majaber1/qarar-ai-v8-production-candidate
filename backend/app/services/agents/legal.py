from app.services.agents.specialist import SpecialistAgent
class LegalAgent(SpecialistAgent):
 name='legal'; display_name_ar='المراجعة القانونية'; description='المراجعة القانونية'; dependencies=('evidence',); instructions='حدد المسائل القانونية والتعاقدية والولاية والمسؤولية التي تحتاج مستشارًا قانونيًا. لا تخترع قانونًا أو بندًا.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'legal_issues': [], 'contract_questions': [], 'counsel_review_required': True},"confidence":0.0,"warnings":[],"sources":[]}
