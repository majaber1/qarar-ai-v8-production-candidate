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

  return <main className="executiveWorkspace">
    <section className="execHero container">
      <div>
        <span className="pill coral">{t('مكتب التنفيذي','Executive office')}</span>
        <h1>{t('القرارات التي تحتاج انتباهك، بدون ضوضاء.','The decisions that need your attention—without the noise.')}</h1>
        <p>{t('راجع التوصية، مستوى الثقة، المخاطر والأثر، ثم اعتمد القرار أو أعده للفريق بسؤال واضح.','Review the recommendation, confidence, risks, and impact. Then approve it or return it with one clear question.')}</p>
      </div>
      <Link className="btn primary" href="/cases/new">＋ {t('إنشاء مشروع أو حالة','Create project or case')}</Link>
    </section>
    <div className="execStats">
      <div><span>{t('بحاجة لمتابعة','Needs follow-up')}</span><strong>{open}</strong><small>{t('حالة مفتوحة','open cases')}</small></div>
      <div><span>{t('جاهز لاعتمادك','Ready for approval')}</span><strong>{awaiting}</strong><small>{t('راجع التوصية اليوم','review today')}</small></div>
      <div><span>{t('تنبيه مخاطر','Risk alert')}</span><strong>{highRisk}</strong><small>{t('أولوية عالية أو حرجة','high or critical priority')}</small></div>
    </div>
    <section className="container execList"><div className="execNotice"><span>✦</span><div><b>{t('ماذا تفعل هنا؟','What do you do here?')}</b><p>{t('افتح أي حالة لمراجعة موجزها التنفيذي. التفاصيل التقنية والتشغيل الحي موجودة في مساحة المشغّل، وليست مطلوبة لاتخاذ القرار.','Open any case to review its executive brief. Technical details and live operations stay in the operator workspace.')}</p></div></div>
      <div className="sectionHead compact"><div><span className="kicker">{t('موجزات جاهزة','Ready briefings')}</span><h2>{t('قرارات أمامك','Decisions on your desk')}</h2></div></div>
      <CaseList base="/executive"/>
    </section>
  </main>
}
