from app.services.agents.specialist import SpecialistAgent
class ArchitectureAgent(SpecialistAgent):
 name='architecture'; display_name_ar='المعمارية المؤسسية'; description='المعمارية المؤسسية'; dependencies=('evidence',); instructions='حدد فجوات الوضع الحالي والمستهدف والتكامل والاعتماديات. لا تخترع مخططًا.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'current_state_gaps': [], 'target_state_questions': [], 'integration_dependencies': []},"confidence":0.0,"warnings":[],"sources":[]}
