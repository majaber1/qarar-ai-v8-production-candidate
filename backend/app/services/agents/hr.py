from app.services.agents.specialist import SpecialistAgent
class HrAgent(SpecialistAgent):
 name='hr'; display_name_ar='الأثر على الفريق'; description='الأثر على الفريق'; dependencies=('evidence',); instructions='حدد المهارات والتدريب والأدوار وإدارة التغيير. لا تخترع بيانات موظفين.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'skills_needed': [], 'training_needed': [], 'role_impacts': []},"confidence":0.0,"warnings":[],"sources":[]}
