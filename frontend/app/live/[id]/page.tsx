"use client";

import Link from "next/link";
import {useParams} from "next/navigation";
import {useEffect,useMemo,useRef,useState} from "react";
import {api,QCase,streamAnalyze} from "@/lib/api";

type NodeState={
  name:string;display:string;stage:string;status:"waiting"|"running"|"done"|"failed"|"skipped";
  source?:string;duration_ms?:number;confidence?:number;cost?:number;tokens?:number;error?:string;
};

type Stage={id:string;label:string;agents:string[]};

const fixedNames:Record<string,string>={
  scoring:"محرك التقييم",options:"بناء البدائل",critic:"المراجع المستقل",chief_advisor:"المستشار التنفيذي"
};

function money(v:number|undefined){return `$${(v||0).toFixed(4)}`}
function seconds(ms:number|undefined){return ms?`${(ms/1000).toFixed(1)} ث`:'—'}

export default function LiveRun(){
  const{id}=useParams<{id:string}>();
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
              initial[name]={name,display:ev.display_names?.[name]||fixedNames[name]||name,stage:s.id,status:"waiting"};
            }
          }
          setNodes(initial);
        }
        if(ev.type==="agent_start"){
          setNodes(prev=>({...prev,[ev.agent]:{...(prev[ev.agent]||{name:ev.agent,display:ev.display_name||fixedNames[ev.agent]||ev.agent}),stage:ev.stage,status:"running",source:ev.source}}));
        }
        if(ev.type==="agent_done"){
          setNodes(prev=>({...prev,[ev.agent]:{...(prev[ev.agent]||{name:ev.agent,display:ev.display_name||fixedNames[ev.agent]||ev.agent}),stage:ev.stage,status:ev.status==="failed"?"failed":"done",source:ev.source,duration_ms:ev.duration_ms,confidence:ev.confidence,cost:ev.estimated_cost_usd,tokens:ev.total_tokens,error:ev.error}}));
          setTotalCost(v=>v+(Number(ev.estimated_cost_usd)||0));
          setTotalTokens(v=>v+(Number(ev.total_tokens)||0));
        }
        if(ev.type==="complete"){
          setTotalCost(Number(ev.estimated_cost_usd)||0);setTotalTokens(Number(ev.total_tokens)||0);setFinished(true);
        }
        if(ev.type==="fatal_error")setError(ev.message||"تعذر إكمال التشغيل");
      });
      setCase(await api.get(id));
    }catch(e){setError(String(e));}
    finally{setRunning(false);setFinished(true);}
  }

  useEffect(()=>{
    if(theCase&&!startedRef.current){startedRef.current=true;start();}
  },[theCase]);

  if(!theCase)return <main className="container">{error||"جارٍ تجهيز جلسة القرار..."}</main>;

  return <main className="container livePage">
    <section className="liveHero">
      <div><span className="kicker light">LIVE DECISION RUN</span><h1>{theCase.title}</h1><p>المجلس يشغّل فقط الخبراء الذين تحتاجهم هذه القضية، ويعرض التنفيذ لحظة بلحظة.</p></div>
      <div className={`livePulse ${running?"on":""}`}><i></i><span>{running?"يعمل الآن":finished?"اكتمل":"جاهز"}</span></div>
    </section>

    <section className="liveMetrics">
      <div><span>المدة الكلية</span><b>{(elapsed/1000).toFixed(1)} ث</b></div>
      <div><span>التكلفة التقديرية</span><b>{money(totalCost)}</b><small>وفق أسعار التخطيط المضبوطة</small></div>
      <div><span>Tokens</span><b>{totalTokens.toLocaleString()}</b></div>
      <div><span>المنجز</span><b>{doneCount}</b><small>{activeCount?`${activeCount} يعمل الآن`:""}</small></div>
    </section>

    {error&&<div className="liveError">{error}</div>}

    <section className="boardGraph">
      {stages.map((stage,si)=>stage.agents.length>0&&<div className="graphStage" key={stage.id}>
        <div className="stageLabel"><span>0{si+1}</span><b>{stage.label}</b></div>
        <div className={`stageNodes ${stage.agents.length>1?"parallel":""}`}>
          {stage.agents.map(name=>{
            const n=nodes[name]||{name,display:fixedNames[name]||name,stage:stage.id,status:"waiting"};
            return <div className={`agentNode ${n.status}`} key={name}>
              <div className="nodeStatus"><i></i><span>{n.status==="running"?"يعمل":n.status==="done"?"اكتمل":n.status==="failed"?"فشل":"بانتظار دوره"}</span></div>
              <h3>{n.display}</h3><code>{name}</code>
              <div className="nodeStats"><span>{n.source||"—"}</span><span>{seconds(n.duration_ms)}</span><span>{money(n.cost)}</span></div>
              {n.confidence!==undefined&&<div className="confidenceBar"><i style={{width:`${Math.round(n.confidence*100)}%`}}></i></div>}
            </div>
          })}
        </div>
        {si<stages.length-1&&<div className="stageArrow">↓</div>}
      </div>)}
      {!stages.length&&<div className="graphPreparing"><div className="spinner"></div><b>الـPlanner يحدد الخبراء المناسبين...</b></div>}
    </section>

    <section className="liveFootGrid">
      <div className="card"><h3>تم اختيارهم</h3>{selected.map(n=><span className="badge gold" key={n}>{n}</span>)}</div>
      <div className="card"><h3>تم تجاوزهم</h3><p className="muted">لن نستهلك وقتًا أو تكلفة عليهم.</p>
        <div className="skipList">{skipped.map(n=><div className="skipRow" key={n}><span className="badge">{n}</span><small>{skipReasons[n]||"غير مرتبط بهذه القضية"}</small></div>)}</div>
      </div>
    </section>

    {finished&&<div className="liveDone"><b>اكتملت جلسة القرار.</b><div><Link className="btn gold" href={`/project/${id}`}>عرض تقرير مدير المشروع</Link> <Link className="btn soft" href={`/developer/${id}`}>التفاصيل التقنية</Link></div></div>}
  </main>
}
