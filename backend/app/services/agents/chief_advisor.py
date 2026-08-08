from app.services.agents.specialist import SpecialistAgent
class ChiefAdvisorAgent(SpecialistAgent):
 name='chief_advisor';display_name_ar='المستشار التنفيذي';description='التوصية التنفيذية';dependencies=('options','critic')
 instructions='استخدم التقارير والدرجات والمراجعة فقط. لا تضف حقائق. قدّم توصية تنفيذية قصيرة جدًا أو أوصِ بتأجيل القرار. ركز على القرار، لماذا، ماذا يفعل المدير الآن، وأهم المخاطر أو الشروط. الإنسان صاحب القرار النهائي.'
 schema={'status':'success|partial','headline':'','summary':'','findings':[],'data':{'decision_label':'','recommended_option_id':'','why':[],'next_actions':[],'top_risks':[],'decision_conditions':[],'confidence':0.0,'human_decision_required':True},'confidence':0.0,'warnings':[],'sources':[]}
