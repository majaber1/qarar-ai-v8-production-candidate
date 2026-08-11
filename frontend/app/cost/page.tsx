'use client';

import{useMemo,useState}from'react';
import{useLang}from'@/components/LanguageProvider';

type SliderProps={label:string;value:number;min:number;max:number;onChange:(value:number)=>void;suffix?:string};

function Slider({label,value,min,max,onChange,suffix}:SliderProps){
  return <label className="slider"><span>{label}<b><span dir="ltr">{value.toLocaleString()}</span>{suffix}</b></span><input aria-label={label} type="range" min={min} max={max} value={value} onChange={event=>onChange(Number(event.target.value))}/></label>;
}

export default function Cost(){
  const{t}=useLang();
  const[decisions,setDecisions]=useState(250);
  const[users,setUsers]=useState(25);
  const[calls,setCalls]=useState(4);
  const[infra,setInfra]=useState(150);
  const[margin,setMargin]=useState(75);
  const costs=useMemo(()=>{
    const ai=decisions*calls*((7000/1e6)*1.25+(2500/1e6)*10);
    const total=ai+infra;
    return{ai,total,decision:total/decisions,user:total/users,price:total/(1-margin/100)};
  },[decisions,users,calls,infra,margin]);

  return <main className="container">
    <div className="pageTitle"><span className="kicker">{t('العمليات المالية لقرار','Qarar FinOps')}</span><h1>{t('استوديو تكلفة العميل','Customer cost studio')}</h1><p>{t('اختبر اقتصاديات الوحدة قبل تقديم العرض. القيم أدناه افتراضات تخطيط قابلة للتعديل وليست قائمة أسعار تجارية.','Model unit economics before you quote. The values below are editable planning assumptions, not a commercial price list.')}</p></div>
    <div className="costLayout"><section className="card" aria-label={t('افتراضات التكلفة','Cost assumptions')}>
      <Slider label={t('القرارات شهريًا','Decisions per month')} value={decisions} min={10} max={5000} onChange={setDecisions}/>
      <Slider label={t('مستخدمو العميل','Customer users')} value={users} min={1} max={500} onChange={setUsers}/>
      <Slider label={t('متوسط استدعاءات الخبراء لكل قرار','Average expert calls per decision')} value={calls} min={1} max={12} onChange={setCalls}/>
      <Slider label={t('البنية التحتية شهريًا','Infrastructure per month')} value={infra} min={0} max={3000} onChange={setInfra} suffix=" USD"/>
      <Slider label={t('هامش الربح الإجمالي المستهدف','Target gross margin')} value={margin} min={40} max={90} onChange={setMargin} suffix="%"/>
    </section><section>
      <div className="metricPanel"><span>{t('التكلفة الشهرية التقديرية','Estimated monthly COGS')}</span><strong dir="ltr">${costs.total.toFixed(0)}</strong><small dir="ltr">AI ${costs.ai.toFixed(0)} + Infrastructure ${infra}</small></div>
      <div className="miniMetrics"><div><b dir="ltr">${costs.decision.toFixed(2)}</b><span>{t('تكلفة القرار','Cost per decision')}</span></div><div><b dir="ltr">${costs.user.toFixed(2)}</b><span>{t('تكلفة المستخدم','Cost per user')}</span></div><div><b dir="ltr">${costs.price.toFixed(0)}</b><span>{t('السعر الأدنى','Minimum price')} @ {margin}% GM</span></div></div>
      <div className="card note"><b>{t('قاعدة تجارية','Commercial rule')}</b><p>{t('سعّر قيمة القرار والحوكمة، لا عدد الرموز. استخدم هذا النموذج لحماية الهامش وتحديد حدود الاستخدام العادل والعملاء الذين يحتاجون بنية مخصصة.','Price the decision value and governance layer—not tokens. Use this model to protect margin, define fair-use limits, and identify customers that need dedicated infrastructure.')}</p></div>
    </section></div>
  </main>;
}
