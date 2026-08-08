'use client';
import {useParams} from 'next/navigation';
import {useCase,Header,ClarificationGate} from '@/components/CaseShell';
import {useLang} from '@/components/LanguageProvider';
function List({items}:{items?:string[]}){return <ul>{(items||[]).map((x,i)=><li key={i}>{x}</li>)}</ul>}
export default function ProjectCaseView(){
  const{id}=useParams<{id:string}>();
  const{x,busy,err,analyze,clarify}=useCase(id);
  const{t}=useLang();
  if(!x)return <main className="container">{err||t('جارٍ التحميل...','Loading...')}</main>;
  const a=x.analysis||{},results=x.agent_results||{};
  const experts=Object.entries(results).filter(([n])=>!["options","scoring","critic","chief_advisor"].includes(n));
  return <main className="container projectCase">
    <Header x={x} busy={busy} analyze={analyze}/>
    <ClarificationGate x={x} busy={busy} clarify={clarify}/>
    {x.clarification_answers&&Object.keys(x.clarification_answers).length>0&&<section className="card clarificationDone">
      <span className="kicker">CLARIFICATIONS PROVIDED</span>
      {Object.entries(x.clarification_answers).map(([q,a],i)=><div key={i} className="clarAnswerItem">
        <b>{q}</b><p>{a}</p>
      </div>)}
    </section>}
    {a.executive&&<><div className="grid g4 pmSummary">
      <div className="card"><span>{t('القرار المقترح','Recommendation')}</span><b>{a.executive.decision}</b></div>
      <div className="card"><span>{t('جاهزية المعلومات','Evidence readiness')}</span><div className="metric">{a.readiness}</div></div>
      <div className="card"><span>{t('المعلومات الناقصة','Missing inputs')}</span><div className="metric">{a.unknowns?.length||0}</div></div>
      <div className="card"><span>{t('التكلفة التقديرية','Estimated AI cost')}</span><div className="metric">${Number(a.run_metrics?.estimated_cost_usd||0).toFixed(3)}</div></div>
    </div>
    <div className="sectionHead"><div><span className="kicker">EVIDENCE GAPS</span><h2>{t('ما الذي ما زلنا نحتاج معرفته؟','What do we still need to know?')}</h2></div></div>
    <div className="card"><List items={a.unknowns}/></div>
    <div className="sectionHead"><div><span className="kicker">SPECIALISTS</span><h2>{t('الخبراء الذين احتاجتهم هذه القضية','Specialists this case actually needed')}</h2></div></div>
    <div className="grid g3">{experts.map(([name,r]:[string,any])=><div className="card expert" key={name}>
      <div className="expert-top"><h3>{r.headline||name}</h3><span className="badge gold">{Math.round((r.confidence||0)*100)}%</span></div>
      <p>{r.summary}</p>
      <span className="badge">{r.status}</span><span className="badge">{r.metadata?.analysis_source||'—'}</span>
    </div>)}</div>
    <div className="sectionHead"><div><span className="kicker">OPTIONS</span><h2>{t('البدائل والمفاضلة','Options & trade-offs')}</h2></div></div>
    <div className="grid g3">{(a.options||[]).map((o:any)=><div className="card option" key={o.id}>
      <span className="badge gold">{o.id}</span><h3>{o.title}</h3><div className="score">{o.weighted_score}/100</div>
      <p>{o.description}</p><h4>{t('الفوائد','Benefits')}</h4><List items={o.benefits}/><h4>{t('المخاطر','Risks')}</h4><List items={o.risks}/>
    </div>)}</div></>}
  </main>
}
