"use client";

import Link from "next/link";
import {useParams} from "next/navigation";
import {useEffect,useMemo,useRef,useState} from "react";
import {api,QCase,streamAnalyze} from "@/lib/api";
import {useLang} from "@/components/LanguageProvider";

type NodeState={
  name:string;display:string;stage:string;status:"waiting"|"running"|"done"|"failed"|"skipped";
  source?:string;duration_ms?:number;confidence?:number;cost?:number;tokens?:number;error?:string;
};

type Stage={id:string;label:string;agents:string[]};

const fixedNames:Record<string,[string,string]>={
  scoring:["محرك التقييم","Scoring engine"],options:["بناء البدائل","Option builder"],critic:["المراجع المستقل","Independent critic"],chief_advisor:["المستشار التنفيذي","Chief advisor"]
};

function money(value:number|undefined){return `$${(value||0).toFixed(4)}`}

export default function LiveRun(){
  const{id}=useParams<{id:string}>();
  const{lang,t,locale}=useLang();
  const displayName=(name:string)=>fixedNames[name]?.[lang==='ar'?0:1]||name;
  const seconds=(milliseconds:number|undefined)=>milliseconds?`${(milliseconds/1000).toFixed(1)} ${t('ث','s')}`:'—';
  const[theCase,setCase]=useState<QCase|null>(null);
  const[stages,setStages]=useState<Stage[]>([]);
  const[nodes,setNodes]=useState<Record<string,NodeState>>({});
  const[selected,setSelected]=useState<string[]>([]);
  const[skipped,setSkipped]=useState<string[]>([]);
  const[skipReasons,setSkipReasons]=useState<Record<string,string>>({});
  const[running,setRunning]=useState(false);
  const[finished,setFinished]=useState(false);
  const[error,setError]=useState("");
  const[totalCost,setTotalCost]=useState(0);
  const[totalTokens,setTotalTokens]=useState(0);
  const[startedAt,setStartedAt]=useState<number|undefined>();
  const[elapsed,setElapsed]=useState(0);
  const startedRef=useRef(false);

  useEffect(()=>{api.get(id).then(setCase).catch(e=>setError(String(e)))},[id]);
  useEffect(()=>{
    if(!running||!startedAt)return;
    const t=setInterval(()=>setElapsed(Date.now()-startedAt),250);
    return()=>clearInterval(t);
  },[running,startedAt]);

  const doneCount=useMemo(()=>Object.values(nodes).filter(n=>n.status==="done").length,[nodes]);
  const activeCount=useMemo(()=>Object.values(nodes).filter(n=>n.status==="running").length,[nodes]);

  async function start(){
    if(running)return;
    setError("");setRunning(true);setFinished(false);setStartedAt(Date.now());setElapsed(0);
    setNodes({});setStages([]);setTotalCost(0);setTotalTokens(0);setSelected([]);setSkipped([]);
    try{
      await streamAnalyze(id,(ev:any)=>{
        if(ev.type==="plan"){
          setSelected(ev.selected_agents||[]);setSkipped(ev.skipped_agents||[]);setSkipReasons(ev.skip_reasons||{});setStages(ev.stages||[]);
          const initial:Record<string,NodeState>={};
          for(const s of ev.stages||[]){
            for(const name of s.agents||[]){
              initial[name]={name,display:ev.display_names?.[name]||displayName(name),stage:s.id,status:"waiting"};
            }
          }
          setNodes(initial);
        }
        if(ev.type==="agent_start"){
          setNodes(prev=>({...prev,[ev.agent]:{...(prev[ev.agent]||{name:ev.agent,display:ev.display_name||displayName(ev.agent)}),stage:ev.stage,status:"running",source:ev.source}}));
        }
        if(ev.type==="agent_done"){
          setNodes(prev=>({...prev,[ev.agent]:{...(prev[ev.agent]||{name:ev.agent,display:ev.display_name||displayName(ev.agent)}),stage:ev.stage,status:ev.status==="failed"?"failed":"done",source:ev.source,duration_ms:ev.duration_ms,confidence:ev.confidence,cost:ev.estimated_cost_usd,tokens:ev.total_tokens,error:ev.error}}));
          setTotalCost(v=>v+(Number(ev.estimated_cost_usd)||0));
          setTotalTokens(v=>v+(Number(ev.total_tokens)||0));
        }
        if(ev.type==="complete"){
          setTotalCost(Number(ev.estimated_cost_usd)||0);setTotalTokens(Number(ev.total_tokens)||0);setFinished(true);
        }
        if(ev.type==="fatal_error")setError(ev.message||t('تعذر إكمال التشغيل','The decision run could not be completed'));
      });
      setCase(await api.get(id));
    }catch(e){setError(String(e));}
    finally{setRunning(false);setFinished(true);}
  }

  useEffect(()=>{
    if(theCase&&!startedRef.current){startedRef.current=true;start();}
  },[theCase]);

  if(!theCase)return <main className="container" aria-live="polite">{error||t('جارٍ تجهيز جلسة القرار...','Preparing the decision session...')}</main>;

  return <main className="container livePage">
    <section className="liveHero">
      <div><span className="kicker light">{t('تشغيل القرار المباشر','Live decision run')}</span><h1>{theCase.title}</h1><p>{t('المجلس يشغّل فقط الخبراء الذين تحتاجهم هذه القضية، ويعرض التنفيذ لحظة بلحظة.','The council activates only the experts this case needs and shows progress as it happens.')}</p></div>
      <div className={`livePulse ${running?"on":""}`} role="status"><i></i><span>{running?t('يعمل الآن','Running'):finished?t('اكتمل','Completed'):t('جاهز','Ready')}</span></div>
    </section>

    <section className="liveMetrics">
      <div><span>{t('المدة الكلية','Total duration')}</span><b dir="ltr">{(elapsed/1000).toFixed(1)} {t('ث','s')}</b></div>
      <div><span>{t('التكلفة التقديرية','Estimated cost')}</span><b dir="ltr">{money(totalCost)}</b><small>{t('وفق أسعار التخطيط المضبوطة','Based on configured planning rates')}</small></div>
      <div><span>{t('الرموز','Tokens')}</span><b dir="ltr">{totalTokens.toLocaleString(locale)}</b></div>
      <div><span>{t('المنجز','Completed')}</span><b>{doneCount}</b><small>{activeCount?`${activeCount} ${t('يعمل الآن','running')}`:""}</small></div>
    </section>

    {error&&<div className="liveError">{error}</div>}

    <section className="boardGraph">
      {stages.map((stage,si)=>stage.agents.length>0&&<div className="graphStage" key={stage.id}>
        <div className="stageLabel"><span>0{si+1}</span><b>{stage.label}</b></div>
        <div className={`stageNodes ${stage.agents.length>1?"parallel":""}`}>
          {stage.agents.map(name=>{
            const n=nodes[name]||{name,display:displayName(name),stage:stage.id,status:"waiting"};
            return <div className={`agentNode ${n.status}`} key={name}>
              <div className="nodeStatus"><i></i><span>{n.status==="running"?t('يعمل','Running'):n.status==="done"?t('اكتمل','Completed'):n.status==="failed"?t('فشل','Failed'):t('بانتظار دوره','Waiting')}</span></div>
              <h3>{n.display}</h3><code>{name}</code>
              <div className="nodeStats"><span>{n.source||"—"}</span><span>{seconds(n.duration_ms)}</span><span>{money(n.cost)}</span></div>
              {n.confidence!==undefined&&<div className="confidenceBar"><i style={{width:`${Math.round(n.confidence*100)}%`}}></i></div>}
            </div>
          })}
        </div>
        {si<stages.length-1&&<div className="stageArrow">↓</div>}
      </div>)}
      {!stages.length&&<div className="graphPreparing" role="status"><div className="spinner"></div><b>{t('يحدد المخطط الخبراء المناسبين...','The planner is selecting the right experts...')}</b></div>}
    </section>

    <section className="liveFootGrid">
      <div className="card"><h3>{t('الخبراء المختارون','Selected experts')}</h3>{selected.map(n=><span className="badge gold" key={n}>{n}</span>)}</div>
      <div className="card"><h3>{t('الخبراء المتجاوزون','Skipped experts')}</h3><p className="muted">{t('لن نستهلك وقتًا أو تكلفة عليهم.','They will not consume time or cost.')}</p>
        <div className="skipList">{skipped.map(n=><div className="skipRow" key={n}><span className="badge">{n}</span><small>{skipReasons[n]||t('غير مرتبط بهذه القضية','Not relevant to this case')}</small></div>)}</div>
      </div>
    </section>

    {finished&&<div className="liveDone" role="status"><b>{t('اكتملت جلسة القرار.','The decision session is complete.')}</b><div><Link className="btn gold" href={`/project/${id}`}>{t('عرض تقرير مدير المشروع','View project manager report')}</Link> <Link className="btn soft" href={`/developer/${id}`}>{t('التفاصيل التقنية','Technical details')}</Link></div></div>}
  </main>
}
