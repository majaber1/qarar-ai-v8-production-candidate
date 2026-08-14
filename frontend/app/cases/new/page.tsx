'use client';

import {FormEvent,useEffect,useState} from 'react';
import Link from 'next/link';
import {useRouter} from 'next/navigation';
import DecisionJourney from '@/components/DecisionJourney';
import {useLang} from '@/components/LanguageProvider';
import {api,QProject} from '@/lib/api';

const types=[
  ['problem','⚠','حل مشكلة','Solve a problem'],
  ['option','⇄','تقييم خيار أو مبادرة','Assess an option'],
  ['inquiry','؟','استفسار تنفيذي','Executive inquiry'],
];

export default function NewCase(){
  const router=useRouter();
  const{lang,t}=useLang();
  const[type,setType]=useState('problem');
  const[projects,setProjects]=useState<QProject[]>([]);
  const[busy,setBusy]=useState(false);
  const[error,setError]=useState('');

  useEffect(()=>{api.projects().then(setProjects).catch(()=>{})},[]);

  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();setBusy(true);setError('');
    const form=new FormData(event.currentTarget);
    const project=String(form.get('project_id')||'');
    try{
      const decision=await api.create({
        project_id:project?Number(project):null,
        title:form.get('title'),description:`[${type}] ${form.get('description')}`,
        urgency:form.get('urgency'),category:type,language:lang,
      });
      router.push(`/project/${decision.id}`);
    }catch{
      setError(t('تعذر إنشاء الحالة. تأكد من تسجيل الدخول واتصال النظام.','Could not create the case. Check your session and system connection.'));
      setBusy(false);
    }
  }

  return <main className="createFlow container">
    <div className="breadcrumb"><Link href="/project">{t('مساحة المشغّل','Operator workspace')}</Link><span>/</span>{t('حالة جديدة','New case')}</div>
    <header className="createHeader">
      <span className="pill blue">{t('القرار · الخطوة الأولى','Decision · first step')}</span>
      <h1>{t('ما القرار الذي تريد اتخاذه؟','What decision are you making?')}</h1>
      <p>{t('ابدأ بالقرار المحدد. سنرشدك لإكمال السياق والبدائل والمعايير والأدلة قبل التحليل.','Start with the specific decision. We will guide you through context, options, criteria, and evidence before analysis.')}</p>
      <DecisionJourney compact/>
    </header>
    <div className="createLayout">
      <form className="decisionForm" onSubmit={submit}>
        <div className="caseTypeGrid">{types.map(item=><button type="button" aria-pressed={type===item[0]} className={`caseType ${type===item[0]?'selected':''}`} onClick={()=>setType(item[0])} key={item[0]}><i aria-hidden="true">{item[1]}</i><b>{t(item[2],item[3])}</b></button>)}</div>
        <div className="conceptHint"><b>{t('المشروع أم حالة القرار؟','Project or decision case?')}</b><p>{t('المشروع يجمع العمل المرتبط بمبادرة واحدة؛ حالة القرار هي القرار المحدد الذي سيحلله قرار.','A project groups work for one initiative; a decision case is the specific decision Qarar will analyze.')}</p></div>
        <div className="field"><label>{t('المشروع','Project')}</label><select name="project_id"><option value="">{t('حالة مستقلة بدون مشروع','Standalone case')}</option>{projects.map(project=><option value={project.id} key={project.id}>{project.name}</option>)}</select>{!projects.length&&<small><Link href="/projects/new">{t('أنشئ مشروعًا أولًا','Create a project first')} ←</Link></small>}</div>
        <div className="field"><label>{t('عنوان مختصر وواضح','A short, clear title')}</label><input name="title" required minLength={3}/></div>
        <div className="field"><label>{t('اشرح الوضع والنتيجة التي تحتاجها','Describe the situation and outcome needed')}</label><textarea name="description" required minLength={10}/></div>
        <div className="field"><label>{t('درجة الاستعجال','Urgency')}</label><select name="urgency" defaultValue="medium"><option value="low">{t('عادية','Normal')}</option><option value="medium">{t('مهمة','Important')}</option><option value="high">{t('عاجلة','Urgent')}</option><option value="critical">{t('حرجة','Critical')}</option></select></div>
        {error&&<div className="errorBox">{error}</div>}
        <div className="formActions"><Link className="btn secondary" href="/project">{t('إلغاء','Cancel')}</Link><button className="btn primary" disabled={busy}>{busy?t('جارٍ الإنشاء...','Creating...'):t('إنشاء الحالة والمتابعة','Create case and continue')}</button></div>
      </form>
      <aside className="createHelp"><b>{t('ماذا سيحدث بعد ذلك؟','What happens next?')}</b><ol><li>{t('نراجع السياق ونطلب المعلومات المهمة فقط.','We review context and ask only for important details.')}</li><li>{t('تضيف البدائل والمعايير والأدلة.','You add options, criteria, and evidence.')}</li><li>{t('يقارن مجلس التحليل القرار من عدة زوايا.','The Decision Analysis Council compares multiple perspectives.')}</li><li>{t('تحصل على توصية واعتماد وخطة عمل.','You receive a recommendation, approval, and action plan.')}</li></ol></aside>
    </div>
  </main>;
}
