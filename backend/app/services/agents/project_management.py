from app.services.agents.specialist import SpecialistAgent
class ProjectManagementAgent(SpecialistAgent):
 name='project_management'; display_name_ar='إدارة المشروع'; description='إدارة المشروع'; dependencies=('evidence',); instructions='حدد الحالة المطلوبة والمعوقات والمالك والمعالم والموارد والتصعيد. لا تخترع تقدمًا.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'status_gaps': [], 'blockers': [], 'ownership_gaps': [], 'milestones_needed': []},"confidence":0.0,"warnings":[],"sources":[]}
