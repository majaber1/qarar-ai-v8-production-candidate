from app.services.agents.specialist import SpecialistAgent
class CriticAgent(SpecialistAgent):
 name='critic';display_name_ar='المراجع المستقل';description='اختبار التوصية';dependencies=('options',)
 instructions='اختبر البدائل والترتيب وابحث عن الأدلة الضعيفة والافتراضات والتحيز والبدائل المفقودة وما الذي قد يعكس الترتيب. لا تعط التوصية النهائية.'
 schema={'status':'success|partial','headline':'','summary':'','findings':[],'data':{'challenges':[],'hidden_assumptions':[],'reversal_conditions':[]},'confidence':0.0,'warnings':[],'sources':[]}
