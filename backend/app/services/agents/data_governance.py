from app.services.agents.specialist import SpecialistAgent
class DataGovernanceAgent(SpecialistAgent):
 name='data_governance'; display_name_ar='حوكمة البيانات'; description='حوكمة البيانات'; dependencies=('evidence',); instructions='حدد التصنيف والإقامة والاحتفاظ والمشاركة والملكية التي يجب التحقق منها.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'classification_questions': [], 'residency_questions': [], 'retention_questions': []},"confidence":0.0,"warnings":[],"sources":[]}
