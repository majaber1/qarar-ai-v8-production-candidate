'use client';
import {useParams} from 'next/navigation';
import {useCase,Header} from '@/components/CaseShell';
import {useLang} from '@/components/LanguageProvider';

export default function View(){
  const{id}=useParams<{id:string}>();
  const{x,busy,err,analyze}=useCase(id);
  const{t}=useLang();
  if(!x)return <main className="container">{err||t('جارٍ التحميل...','Loading...')}</main>;
  const metrics=x.analysis?.run_metrics||{};
  return <main className="container">
    <Header x={x} busy={busy} analyze={analyze}/>
    <div className="devMetrics">
      <div className="card"><span>{t('المصدر','Provider')}</span><b className="metric">{x.analysis_source||'—'}</b></div>
      <div className="card"><span>{t('التكلفة','Cost')}</span><b className="metric">${Number(metrics.estimated_cost_usd||0).toFixed(4)}</b></div>
      <div className="card"><span>Tokens</span><b className="metric">{Number(metrics.total_tokens||0).toLocaleString()}</b></div>
      <div className="card"><span>{t('المدة','Duration')}</span><b className="metric">{metrics.elapsed_ms?`${(metrics.elapsed_ms/1000).toFixed(1)}s`:'—'}</b></div>
    </div>
    <div className="grid g2" style={{marginTop:18}}>
      <div className="card"><h2>{t('تم اختيارهم','Selected Agents')}</h2>
        {(x.selected_agents||[]).map(n=><span className="badge gold" key={n}>{n}</span>)}
      </div>
      <div className="card"><h2>{t('تم تجاوزهم','Skipped Agents')}</h2>
        {(x.skipped_agents||[]).map(n=><span className="badge" key={n}>{n}</span>)}
      </div>
    </div>
    <h2 className="section">{t('سجل التنفيذ','Execution audit')}</h2>
    <div className="card audit">
      <div className="audit-row"><b>Agent</b><b>Source</b><b>Status</b><b>Duration</b><b>Confidence</b></div>
      {(x.audit_log||[]).map((r:any,i)=><div className="audit-row" key={i}>
        <span>{r.agent}</span><span>{r.source}</span>
        <span className={r.status==='done'?'statusOk':r.status==='failed'?'statusFail':''}>{r.status}</span>
        <span>{r.duration_ms} ms</span><span>{Math.round((r.confidence||0)*100)}%</span>
      </div>)}
    </div>
    {x.analysis&&<><h2 className="section">{t('النتائج الكاملة','Full results')}</h2>
    <div className="card"><pre>{JSON.stringify(x.agent_results,null,2)}</pre></div></>}
  </main>
}
