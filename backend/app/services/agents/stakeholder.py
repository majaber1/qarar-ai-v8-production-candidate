from app.services.agents.specialist import SpecialistAgent
class StakeholderAgent(SpecialistAgent):
 name='stakeholder'; display_name_ar='أصحاب العلاقة'; description='أصحاب العلاقة'; dependencies=('evidence',); instructions='حدد المالك والمنفذ والموافق والمتأثرين وفجوات الصلاحية. لا تخترع أسماء.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'known_roles': [], 'missing_roles': [], 'decision_rights': []},"confidence":0.0,"warnings":[],"sources":[]}
