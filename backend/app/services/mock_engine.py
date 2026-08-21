from app.services.contracts import AgentResult,Finding

def mock_result(name,case):
 common=dict(status='partial',confidence=.75,warnings=['mock_fallback'],sources=[],metadata={'analysis_source':'mock'})
 if name=='evidence':
  hits=getattr(case,'evidence_context',[]) or []
  facts=[h.get('text','') for h in hits[:5]] or [case.description]
  sources=[{'source_id':h.get('source_id',i+1),'title':h.get('title',f'Evidence {i+1}'),'source_ref':h.get('source_ref','fabric'),'trust_level':h.get('trust_level','A' if i==0 else 'B')} for i,h in enumerate(hits)] if hits else [{'source_id':1,'title':'وثيقة نطاق القرار والمعايير','source_ref':'case-context','trust_level':'A'}]
  missing=[] if hits else ['المالك المسؤول','النتيجة المطلوبة','الأدلة الداعمة']
  return AgentResult(name,headline='تم ربط الأدلة' if hits else 'المعلومات تحتاج استكمال',summary='تم استخدام أدلة Knowledge Fabric.' if hits else 'تم استلام وصف القضية لكن الأدلة المستقلة غير متاحة بعد.',findings=[Finding('دليل مسترجع' if hits else 'وصف القضية',f,verified=bool(hits)) for f in facts],data={'facts':facts,'claims':[],'assumptions':[],'missing_information':missing,'required_evidence':[] if hits else ['آخر تقرير حالة'],'readiness':'high' if hits else 'low'},sources=sources,**{k:v for k,v in common.items() if k!='sources'})
 if name=='risk':return AgentResult(name,headline='مخاطر مدارة وضوابط موصى بها',summary='تم تحليل المخاطر التشغيلية والامتثالية للبدائل المطروحة.',data={'risk_level':'medium','top_risks':['مخاطر الاعتماد على مورد خارجي','مخاطر الجدول الزمني للتنفيذ'],'mitigations':['وضع بوابات تحقق إلزامية','تضمين شروط جزائية في العقد']},**common)
 if name=='options':
  user_opts=getattr(case,'options',None)
  if user_opts and len(user_opts)>0:
   evaluated=[]
   raw_criteria=getattr(case,'scoring_criteria',None) or [{'key':'compliance'},{'key':'risk'},{'key':'financial'},{'key':'time'},{'key':'strategy'},{'key':'stakeholder'}]
   for idx,opt in enumerate(user_opts):
    opt_id=str(opt.get('id') or chr(65+idx))
    title=str(opt.get('title') or f'الخيار {opt_id}')
    desc=str(opt.get('description') or '')
    benefits=list(opt.get('benefits') or [f'تحقيق الأهداف والمزايا المحددة لـ {title}'])
    risks=list(opt.get('risks') or [f'المخاطر التشغيلية والتنفيذية لـ {title}'])
    conditions=list(opt.get('conditions') or [f'استيفاء شروط الاعتماد لـ {title}'])
    raw_scores=dict(opt.get('criterion_scores') or {})
    prov_dict=dict(opt.get('criterion_provenance') or {})
    for c in raw_criteria:
     ckey=c['key'] if isinstance(c,dict) else str(c)
     if ckey not in raw_scores:
      base_score=92.0 - (idx * 6.0)
      raw_scores[ckey]=max(45.0,min(98.0,base_score))
    evaluated.append({'id':opt_id,'title':title,'description':desc,'benefits':benefits,'risks':risks,'conditions':conditions,'criterion_scores':raw_scores,'criterion_provenance':prov_dict})
   return AgentResult(name,headline=f'{len(evaluated)} بدائل معتمدة',summary='تم تقييم البدائل المحددة من المستخدم وفق معايير القرار والأدلة المتاحة.',data={'options':evaluated},**common)
  return AgentResult(name,headline='ثلاثة بدائل',summary='تم بناء ثلاثة مسارات أولية للمفاضلة.',data={'options':[{'id':'A','title':'الاستمرار بضوابط','description':'الاستمرار مع بوابات تحقق ومراقبة مستمرة.','benefits':['الاستمرارية وتفادي التوقف'],'risks':['نقص الأدلة التفصيلية'],'conditions':['تحديد المالك المسؤول'],'criterion_scores':{'compliance':65,'risk':55,'financial':70,'time':80,'strategy':70,'stakeholder':65}},{'id':'B','title':'مراجعة قصيرة قبل الالتزام','description':'استكمال الأدلة الحرجة ثم اعتماد القرار.','benefits':['جودة قرار أعلى ومخاطر أقل'],'risks':['تأخير محدود في الجدول'],'conditions':['جمع أدلة التحقق'],'criterion_scores':{'compliance':85,'risk':80,'financial':60,'time':55,'strategy':80,'stakeholder':75}},{'id':'C','title':'إعادة تصميم المسار','description':'إعادة تصميم النطاق والحلول المتأثرة.','benefits':['حل جذري مستدام'],'risks':['تكلفة إضافية ووقت أطول'],'conditions':['تأكيد الجدوى الاقتصادية'],'criterion_scores':{'compliance':90,'risk':85,'financial':45,'time':35,'strategy':90,'stakeholder':60}}]},**common)
 if name=='critic':return AgentResult(name,status='success',headline='مراجعة نقدية مستقلة',summary='تم فحص الافتراضات والتحديات لضمان متانة القرار.',data={'challenges':['هل التقديرات المالية شاملة لجميع بنود التكلفة؟','هل شروط البوابات الإلزامية محققة بالكامل؟'],'hidden_assumptions':['افتراض ثبات التكاليف التشغيلية للسنة الأولى'],'reversal_conditions':['ظهور متطلبات تنظيمية جديدة أو إخفاق في فحص الامتثال']},confidence=.85,warnings=[],sources=[],metadata={'analysis_source':'mock'})
 if name=='chief_advisor':
  user_opts=getattr(case,'options',None)
  rec_id=str(user_opts[0].get('id','A')) if (user_opts and len(user_opts)>0) else 'B'
  return AgentResult(name,headline='التوصية التنفيذية المعتمدة',summary='يوصى باعتماد البديل الأعلى تقييمًا بعد التحقق من استيفاء جميع المتطلبات.',data={'decision_label':'اعتماد البديل المتصدر وخطة التنفيذ','recommended_option_id':rec_id,'why':['تحقيق أعلى درجة مرجحة في التقييم المحدد','التوافق مع البوابات الإلزامية ومعايير الامتثال'],'next_actions':['تعيين مسؤول التنفيذ المباشر','توقيع العقود واتفاقيات مستوى الخدمة SLA','جدولة مراجعة دورية لمتابعة النتائج'],'top_risks':['مخاطر التأخير في التسليم','مخاطر إدارة التغيير'],'decision_conditions':['توفر الاعتماد المالي وخطة العمل'],'confidence':.80,'human_decision_required':True},**common)
 return AgentResult(name,headline='تحليل اختصاصي',summary='تم تحليل النطاق بنجاح.',data={},**common)

