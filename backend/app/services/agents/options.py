from app.services.agents.specialist import SpecialistAgent
class OptionsAgent(SpecialistAgent):
 name='options';display_name_ar='البدائل';description='البدائل';dependencies=('evidence','risk')
 instructions='أنشئ ثلاثة بدائل مختلفة فعلاً من التقارير المتاحة. لا تختَر الفائز. لكل بديل عنوان ووصف وفوائد ومخاطر وشروط ودرجات تقديرية للالتزام والمخاطر والمالي والوقت والاستراتيجية وأصحاب العلاقة.'
 schema={'status':'success|partial','headline':'','summary':'','findings':[],'data':{'options':[{'id':'A','title':'','description':'','benefits':[],'risks':[],'conditions':[],'criterion_scores':{'compliance':0,'risk':0,'financial':0,'time':0,'strategy':0,'stakeholder':0}}]},'confidence':0.0,'warnings':[],'sources':[]}
