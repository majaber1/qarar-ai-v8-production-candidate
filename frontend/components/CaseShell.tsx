'use client';
import Link from 'next/link';
import {useEffect,useState} from 'react';
import {api,QCase} from '@/lib/api';
import {useLang} from './LanguageProvider';

export function useCase(id:string){
  const[x,setX]=useState<QCase|null>(null);const[busy,setBusy]=useState(false);const[err,setErr]=useState('');
  useEffect(()=>{api.get(id).then(setX).catch(e=>setErr(String(e)))},[id]);
  async function analyze(){setBusy(true);try{setX(await api.analyze(id))}catch(e){setErr(String(e))}finally{setBusy(false)}}
  async function clarify(answers:Record<string,string>){setBusy(true);try{setX(await api.clarify(id,answers))}catch(e){setErr(String(e))}finally{setBusy(false)}}
  async function approve(option_id:string,decision_owner:string,due_date?:string){setBusy(true);try{setX(await api.approve(id,{option_id,decision_owner,due_date}))}catch(e){setErr(String(e))}finally{setBusy(false)}}
  return{x,busy,err,analyze,clarify,approve,setX};
}

export function Header({x,busy,analyze}:{x:QCase,busy:boolean,analyze:()=>void}){
  const{t,status,urgency}=useLang();
  return <section className="hero caseHero">
    <div style={{display:'flex',gap:8,alignItems:'center',flexWrap:'wrap'}}>
      <span className="badge gold">{urgency(x.urgency)}</span>
      <span className="badge">{status(x.status)}</span>
      {x.approved_option&&<span className="badge gold">{t('الخيار','Option')} {x.approved_option}</span>}
    </div>
    <h1>{x.title}</h1><p>{x.description}</p>
    <div className="runActions">
      <Link className="btn gold" href={`/live/${x.id}`}>{t('تشغيل مباشر ومراقبة المجلس','Run live council')}</Link>
      <button className="btn soft" onClick={analyze} disabled={busy}>{busy?t('يجري التحليل...','Analyzing...'):t('تحليل سريع','Quick analysis')}</button>
      <Link className="btn soft" href={`/knowledge?case=${x.id}`}>{t('الأدلة والأسئلة','Evidence & Q&A')}</Link>
      <span className="badge">{t('المصدر','Source')}: {x.analysis_source||t('لم يُحلل','Not analyzed')}</span>
    </div>
  </section>
}

export function ClarificationGate({x,busy,clarify}:{x:QCase,busy:boolean,clarify:(a:Record<string,string>)=>void}){
  const{t}=useLang();
  const[answers,setAnswers]=useState<Record<string,string>>({});
  if(x.status!=='needs_clarification'||!x.pending_clarifications?.length) return null;
  return <section className="clarificationGate">
    <div className="clarificationHeader">
      <span className="kicker">{t('مطلوب استيضاح','Clarification required')}</span>
      <h2>{t('Qarar يحتاج إجابتك قبل المتابعة','Qarar needs your input before proceeding')}</h2>
      <p className="muted">{t('الأسئلة أدناه لم نتمكن من استنتاجها تلقائيًا من المعرفة المتاحة.','The questions below could not be auto-resolved from available knowledge.')}</p>
    </div>
    {x.pending_clarifications.map((q,i)=><div className="clarificationQ" key={i}>
      <label><span className="num">{i+1}</span> {q}</label>
      <textarea value={answers[q]||''} onChange={e=>setAnswers({...answers,[q]:e.target.value})}
        placeholder={t('اكتب إجابتك هنا...','Type your answer here...')}/>
    </div>)}
    <button className="btn gold" disabled={busy||Object.values(answers).every(v=>!v.trim())}
      onClick={()=>clarify(answers)}>
      {busy?t('جارٍ الإرسال...','Submitting...'):t('إرسال الإجابات ومتابعة التحليل','Submit answers & continue analysis')}
    </button>
  </section>;
}

export function ApprovalPanel({x,busy,approve}:{x:QCase,busy:boolean,approve:(oid:string,owner:string,due?:string)=>void}){
  const{t}=useLang();
  const[oid,setOid]=useState('');
  const[owner,setOwner]=useState('');
  const[due,setDue]=useState('');
  const options=x.analysis?.options||[];
  if(!['recommendation_ready','pending_approval'].includes(x.status)||!options.length||x.approved_option) return null;
  return <section className="approvalPanel">
    <span className="kicker">{t('الاعتماد التنفيذي','Executive approval')}</span>
    <h2>{t('اعتمد القرار','Approve decision')}</h2>
    <div className="g2" style={{gap:14}}>
      <div className="field"><label>{t('الخيار المعتمد','Approved option')}</label>
        <select value={oid} onChange={e=>setOid(e.target.value)}>
          <option value="">{t('اختر...','Select...')}</option>
          {options.map((o:any)=><option key={o.id} value={o.id}>{o.id}: {o.title} ({o.weighted_score}/100)</option>)}
        </select>
      </div>
      <div className="field"><label>{t('مسؤول التنفيذ','Decision owner')}</label>
        <input value={owner} onChange={e=>setOwner(e.target.value)} placeholder={t('مثال: أحمد الراشد','e.g. Ahmed Al-Rashid')}/>
      </div>
      <div className="field"><label>{t('الموعد النهائي','Due date')}</label>
        <input type="date" value={due} onChange={e=>setDue(e.target.value)}/>
      </div>
    </div>
    <button className="btn gold" disabled={busy||!oid||!owner}
      onClick={()=>approve(oid,owner,due||undefined)}>
      {busy?t('جارٍ الاعتماد...','Approving...'):t('اعتماد رسمي','Formally approve')}
    </button>
  </section>;
}
