'use client';
import {useEffect,useState} from 'react';
import {api} from '@/lib/api';
import {useLang} from '@/components/LanguageProvider';

export default function Page(){
  const{t}=useLang();
  const[d,setD]=useState<any>(null);
  const[out,setOut]=useState<any>(null);
  const[busy,setBusy]=useState('');
  const[err,setErr]=useState('');

  useEffect(()=>{api.connectCatalog().then(setD).catch(e=>setErr(String(e)))},[]);

  async function dry(id:string){
    setBusy(id);setErr('');
    try{setOut(await api.runAutomation({workflow_id:id,payload:{note:'Qarar V8 demo'},dry_run:true}))}
    catch(e){setErr(String(e))}finally{setBusy('')}
  }

  async function run(id:string){
    setBusy(id);setErr('');
    try{setOut(await api.runAutomation({workflow_id:id,payload:{note:'Qarar V8 real'},dry_run:false}))}
    catch(e){setErr(String(e))}finally{setBusy('')}
  }

  return <main className="container">
    <div className="pageTitle"><span className="kicker">QARAR AUTOMATE</span>
      <h1>{t('من القرار إلى التنفيذ، مع بقاء الإنسان مسؤولًا','From decision to action, with humans accountable')}</h1>
      <p>{t('n8n وWebhooks وتجارب Dry-run مجهزة خلف بوابة موافقة بشرية.','n8n, webhooks and dry-runs behind a human approval gate.')}</p>
    </div>
    {err&&<div className="errorBox">{err}</div>}
    <div className="grid g3">
      {(d?.automations||[]).map((x:any)=><div className="card" key={x.id}>
        <h2>{x.name}</h2><p className="muted">{x.description}</p>
        <div style={{display:'flex',gap:8,marginTop:12}}>
          <button className="btn soft" onClick={()=>dry(x.id)} disabled={busy===x.id}>
            {t('تجربة بدون تنفيذ','Dry run')}
          </button>
          <button className="btn gold" onClick={()=>run(x.id)} disabled={busy===x.id}>
            {t('تنفيذ حقيقي','Execute')}
          </button>
        </div>
      </div>)}
    </div>
    {out&&<section className="card automationResult">
      <span className="kicker">{out.dry_run?'DRY RUN RESULT':'EXECUTION RESULT'}</span>
      <div className="automationStatus">
        <span className={`status ${out.status==='executed'?'ok':out.status==='sent'?'planned':'fail'}`}>
          {out.status}
        </span>
        {out.run_id&&<small className="muted">Run ID: {out.run_id}</small>}
      </div>
      <pre>{JSON.stringify(out,null,2)}</pre>
    </section>}
  </main>
}
