'use client';
import {useEffect,useState} from 'react';
import CaseList from '@/components/CaseList';
import {api} from '@/lib/api';
import {useLang} from '@/components/LanguageProvider';

export default function Page(){
  const{t}=useLang();
  const[health,setHealth]=useState<any>(null);
  useEffect(()=>{api.readyz().then(setHealth).catch(()=>setHealth({status:'error'}))},[]);

  return <main className="container">
    <section className="devHero">
      <span className="kicker light">AI OPERATIONS</span>
      <h1>{t('لوحة المطور والإدارة التقنية','Developer & AI Operations')}</h1>
      <p>{t('التوجيه، الوكلاء المتجاوزون، المصدر، الزمن، التكلفة، fallback وسجل التنفيذ.','Routing, skipped agents, provider, latency, cost, fallback and execution audit.')}</p>
    </section>
    <div className="devMetrics">
      <div className="card">
        <span>{t('حالة النظام','System status')}</span>
        <b className="metric" style={{color:health?.status==='ok'?'var(--emerald)':'#b65a5a'}}>{health?.status||'...'}</b>
      </div>
      <div className="card"><span>{t('قاعدة البيانات','Database')}</span><b className="metric">{health?.database||'...'}</b></div>
      <div className="card"><span>Version</span><b className="metric">{health?.version||'...'}</b></div>
      <div className="card"><span>{t('الهوية','Auth')}</span><b className="metric">{health?.auth||'...'}</b></div>
    </div>
    <h2 className="section">{t('القضايا','Cases')}</h2>
    <CaseList base="/developer"/>
  </main>
}
