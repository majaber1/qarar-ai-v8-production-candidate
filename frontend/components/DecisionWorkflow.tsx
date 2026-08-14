'use client';
import {FormEvent,useEffect,useState} from 'react';
import {api,QCase} from '@/lib/api';
import {useLang} from './LanguageProvider';

const human=(value:string)=>value.replaceAll('_',' ');

export default function DecisionWorkflow({x,onChange}:{x:QCase,onChange:(value:QCase)=>void}){
  const{t,status}=useLang();const[busy,setBusy]=useState(false);const[error,setError]=useState('');
  const[sensitivity,setSensitivity]=useState<any>(x.analysis?.sensitivity);const[weights,setWeights]=useState<Record<string,number>>({});
  const[actions,setActions]=useState<any[]>([]);const[outcomes,setOutcomes]=useState<any[]>([]);
  useEffect(()=>{api.actions(String(x.id)).then(setActions).catch(()=>{});api.outcomes(String(x.id)).then(setOutcomes).catch(()=>{})},[x.id]);
  async function transition(status:string){const reason=window.prompt(t('اكتب سبب تغيير الحالة','Enter the reason for this transition'));if(!reason)return;setBusy(true);setError('');try{onChange(await api.transition(String(x.id),status,reason))}catch(e){setError(String(e))}finally{setBusy(false)}}
  async function runSensitivity(){setBusy(true);setError('');try{setSensitivity(await api.sensitivity(String(x.id),weights))}catch(e){setError(String(e))}finally{setBusy(false)}}
  async function addAction(event:FormEvent<HTMLFormElement>){event.preventDefault();const target=event.currentTarget;const form=new FormData(target);setBusy(true);try{const item=await api.createAction(String(x.id),{title:form.get('title'),owner:form.get('owner'),priority:form.get('priority'),due_date:form.get('due_date')||null,source_reference:x.analysis?.executive?.recommended_option_id||null});setActions(current=>[item,...current]);target.reset()}catch(e){setError(String(e))}finally{setBusy(false)}}
  async function completeAction(item:any){try{const updated=await api.updateAction(String(x.id),item.id,{status:'completed'});setActions(current=>current.map(action=>action.id===item.id?updated:action))}catch(e){setError(String(e))}}
  async function addOutcome(event:FormEvent<HTMLFormElement>){event.preventDefault();const target=event.currentTarget;const form=new FormData(target);setBusy(true);try{const item=await api.createOutcome(String(x.id),{result:form.get('result'),expected_result:form.get('expected_result'),actual_result:form.get('actual_result'),lessons_learned:form.get('lessons_learned')||null,corrective_action:form.get('corrective_action')||null,next_review_date:form.get('next_review_date')||null});setOutcomes(current=>[item,...current]);target.reset()}catch(e){setError(String(e))}finally{setBusy(false)}}
  const confidence=x.analysis?.executive?.confidence;const breakdown=x.analysis?.executive?.confidence_breakdown;
  const transitions:Record<string,string[]>={draft:['ready_for_analysis','deferred','archived'],reopened:['ready_for_analysis','deferred','archived'],needs_information:['ready_for_analysis','deferred','archived'],recommendation_ready:['pending_approval','rejected','deferred','archived'],pending_approval:['rejected','deferred','archived'],approved:['reopened','archived'],rejected:['reopened','archived'],deferred:['reopened','archived'],archived:['reopened']};
  return <div className="decisionWorkflow">
    {error&&<div className="inlineError">{error}</div>}
    {typeof confidence==='number'&&<section className="card qualityPanel"><div className="panelHeading"><div><span className="kicker">{t('ثقة قابلة للتفسير','Explainable confidence')}</span><h2>{Math.round(confidence*100)}%</h2></div><span className="badge gold">{breakdown?.method}</span></div>
      <div className="factorGrid">{Object.entries(breakdown?.factors||{}).map(([key,value])=><div key={key}><span>{human(key)}</span><b>{Math.round(Number(value)*100)}%</b><progress max="1" value={Number(value)}/></div>)}</div>
      {!!breakdown?.positive_factors?.length&&<p><b>{t('عوامل القوة:','Positive factors:')}</b> {breakdown.positive_factors.map(human).join('، ')}</p>}
      {!!breakdown?.improvement_actions?.length&&<p><b>{t('لرفع الثقة:','To improve confidence:')}</b> {breakdown.improvement_actions.join('، ')}</p>}
    </section>}
    {!!x.analysis?.scoring_criteria?.length&&<section className="card qualityPanel"><div className="panelHeading"><div><span className="kicker">{t('تحليل الحساسية','Sensitivity analysis')}</span><h2>{t('ما الذي قد يغيّر التوصية؟','What could change the recommendation?')}</h2></div><span className="badge">{sensitivity?.stability==='stable'?t('مستقرة','Stable'):sensitivity?.stability==='moderately_sensitive'?t('متوسطة الحساسية','Moderately sensitive'):sensitivity?.stability==='highly_sensitive'?t('عالية الحساسية','Highly sensitive'):t('لم تُشغّل','Not run')}</span></div>
      <div className="factorGrid">{x.analysis.scoring_criteria.map((criterion:any)=><label key={criterion.key}><span>{criterion.name}</span><input type="number" min="0" step="0.05" defaultValue={criterion.weight} onChange={e=>setWeights(current=>({...current,[criterion.key]:Number(e.target.value)}))}/></label>)}</div>
      <button className="btn soft" disabled={busy} onClick={runSensitivity}>{t('إعادة حساب السيناريو','Recalculate scenario')}</button>
      {sensitivity&&<p>{t('المتصدر الأساسي','Baseline leader')}: <b dir="ltr">{sensitivity.baseline_leader||'—'}</b> · {t('متصدر السيناريو','Scenario leader')}: <b dir="ltr">{sensitivity.scenario_leader||'—'}</b></p>}
    </section>}
    <section className="card qualityPanel"><div className="panelHeading"><div><span className="kicker">{t('دورة القرار','Decision lifecycle')}</span><h2>{t('الحالة والإجراءات الصحيحة','Status and valid actions')}</h2></div><span className="badge">{status(x.status)}</span></div><div className="runActions">{(transitions[x.status]||[]).map(next=><button className="btn soft" disabled={busy} key={next} onClick={()=>transition(next)}>{status(next)}</button>)}</div></section>
    <section className="card qualityPanel"><div className="panelHeading"><div><span className="kicker">{t('خطة التنفيذ','Action plan')}</span><h2>{t('حوّل التوصية إلى عمل','Turn the decision into action')}</h2></div><span className="badge">{actions.filter(a=>a.status!=='completed'&&a.status!=='cancelled').length} {t('مفتوحة','open')}</span></div>
      <form className="workflowForm" onSubmit={addAction}><input name="title" required placeholder={t('عنوان الإجراء','Action title')}/><input name="owner" required placeholder={t('المالك','Owner')}/><select name="priority"><option value="medium">{t('متوسطة','Medium')}</option><option value="high">{t('عالية','High')}</option><option value="low">{t('منخفضة','Low')}</option></select><input name="due_date" type="date"/><button className="btn gold" disabled={busy}>{t('إضافة','Add')}</button></form>
      <div className="workflowList">{actions.map(item=><article key={item.id}><div><b>{item.title}</b><small>{item.owner} · {status(item.status)} · {item.due_date||'—'}</small></div>{item.status!=='completed'&&<button className="btn soft" onClick={()=>completeAction(item)}>{t('إكمال','Complete')}</button>}</article>)}</div>
    </section>
    {x.status==='approved'&&<section className="card qualityPanel"><div className="panelHeading"><div><span className="kicker">{t('النتائج والتعلّم','Outcomes & learning')}</span><h2>{t('المتوقع مقابل الفعلي','Expected versus actual')}</h2></div></div>
      <form className="outcomeForm" onSubmit={addOutcome}><select name="result"><option value="success">{t('نجاح','Success')}</option><option value="partial">{t('جزئي','Partial')}</option><option value="failure">{t('إخفاق','Failure')}</option></select><textarea name="expected_result" required placeholder={t('النتيجة المتوقعة','Expected result')}/><textarea name="actual_result" required placeholder={t('النتيجة الفعلية','Actual result')}/><textarea name="lessons_learned" placeholder={t('الدروس المستفادة','Lessons learned')}/><textarea name="corrective_action" placeholder={t('الإجراء التصحيحي','Corrective action')}/><input name="next_review_date" type="date"/><button className="btn gold" disabled={busy}>{t('حفظ النتيجة','Save outcome')}</button></form>
      <div className="workflowList">{outcomes.map(item=><article key={item.id}><div><b>{human(item.result)}</b><small>{item.actual_result}</small></div></article>)}</div>
    </section>}
  </div>
}
