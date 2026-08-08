from app.services.agents.specialist import SpecialistAgent
class PolicyAgent(SpecialistAgent):
 name='policy'; display_name_ar='الحوكمة والسياسات'; description='الحوكمة والسياسات'; dependencies=('evidence',); instructions='حدد مجالات السياسات والموافقات والقيود التي تحتاج تحققًا. لا تدّع سياسة محددة غير موجودة في المدخلات.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'policy_domains': [], 'required_approvals': [], 'constraints_to_verify': []},"confidence":0.0,"warnings":[],"sources":[]}
