from app.services.agents.specialist import SpecialistAgent
class FinancialAgent(SpecialistAgent):
 name='financial'; display_name_ar='الجانب المالي'; description='الجانب المالي'; dependencies=('evidence',); instructions='استخدم فقط الأرقام المقدمة. لا تخترع تكلفة أو عائدًا. حدد التكاليف ومدخلات TCO وROI الناقصة.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'known_costs': [], 'unknown_costs': [], 'budget_constraints': [], 'tco_inputs': [], 'roi_inputs': []},"confidence":0.0,"warnings":[],"sources":[]}
