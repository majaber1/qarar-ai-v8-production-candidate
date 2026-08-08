'use client';
import Link from 'next/link';
import {useEffect,useState} from 'react';
import {api,QCase} from '@/lib/api';
import CaseList from '@/components/CaseList';
import {useLang} from '@/components/LanguageProvider';

export default function Page(){
  const{t}=useLang();
  const[cases,setCases]=useState<QCase[]>([]);
  useEffect(()=>{api.list().then(setCases).catch(()=>{})},[]);
  const open=cases.filter(c=>!['approved','executed'].includes(c.status)).length;
  const awaiting=cases.filter(c=>c.status==='recommendation_ready').length;
  const highRisk=cases.filter(c=>c.urgency==='critical'||c.urgency==='high').length;

  return <main className="execPage">
    <section className="execHero">
      <div>
        <span className="kicker light">EXECUTIVE DECISION COCKPIT</span>
        <h1>{t('قرارات أسرع. رؤية أوضح. مسؤولية بشرية.','Faster decisions. Clearer judgment. Human accountability.')}</h1>
        <p>{t('واجهة مخصصة للقيادة: التوصية والثقة والمخاطر والخطوة التالية فقط.','A leadership-only view: recommendation, confidence, risk and next action — no agent noise.')}</p>
      </div>
      <Link className="btn gold" href="/cases/new">{t('قرار جديد','New decision')}</Link>
    </section>
    <div className="execStats">
      <div><strong>{open}</strong><span>{t('قرارات مفتوحة','Open decisions')}</span></div>
      <div><strong>{awaiting}</strong><span>{t('بانتظار اعتماد','Awaiting approval')}</span></div>
      <div><strong>{highRisk}</strong><span>{t('مخاطر عالية','High-risk')}</span></div>
    </div>
    <section className="container execList">
      <div className="sectionHead"><div><span className="kicker">DECISIONS</span><h2>{t('موجز القرارات','Decision briefings')}</h2></div></div>
      <CaseList base="/executive"/>
    </section>
  </main>
}
