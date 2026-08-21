'use client';
import {useParams} from 'next/navigation';
import Link from 'next/link';
import {useCase,Header,ApprovalPanel} from '@/components/CaseShell';
import {useLang} from '@/components/LanguageProvider';

function L({items}:{items?:string[]}){return <>{(items||[]).map((x,i)=><div className="action" key={i}><span className="num">{i+1}</span><span>{x}</span></div>)}</>}

export default function View(){
  const{id}=useParams<{id:string}>();
  const{x,busy,err,analyze,approve}=useCase(id);
  const{t}=useLang();
  if(!x)return <main className="container">{err||t('جارٍ التحميل...','Loading...')}</main>;
  const e=x.analysis?.executive;
  return <main className="executiveCase"><div className="container">
    <Header x={x} busy={busy} analyze={analyze}/>
    {e&&<><section className="execDecision">
      <span className="kicker light">{t('الموجز التنفيذي','Executive brief')}</span>
      <h1>{e.decision}</h1>
      <div className="execDecisionMetrics">
        <div><b>{Math.round((e.confidence||0)*100)}%</b><span>{t('الثقة','Confidence')}</span></div>
        <div><b>{x.analysis?.readiness||'—'}</b><span>{t('جاهزية الأدلة','Evidence readiness')}</span></div>
        <div><b>{e.recommended_option_id||'—'}</b><span>{t('الخيار المتصدر','Recommended')}</span></div>
        <div><b>{x.analysis?.sensitivity?.stability === 'stable' ? t('مستقر','Stable') : t('حساس','Sensitive')}</b><span>{t('متانة السيناريوهات','Robustness')}</span></div>
      </div>
    </section>
    {e.recommendation_stale && (
      <section className="card p-4 bg-amber-950/40 border-2 border-amber-500 text-amber-200 text-sm space-y-1 shadow-xl">
        <div className="flex items-center gap-2 font-bold text-amber-300">
          <span className="text-xl">⚠️</span>
          <span>{t('تنبيه: تم تعديل درجات التقييم وتغيرت التوصية الأصلية', 'Notice: Scores were modified, changing the original recommendation')}</span>
        </div>
        <p className="text-xs text-white/90 ps-7">
          {e.stale_reason || t('يرجى مراجعة التوصية المحدثة وإعادة اعتمادها.', 'Please review the recalculated recommendation and submit for approval.')}
        </p>
      </section>
    )}
    <ApprovalPanel x={x} busy={busy} approve={approve}/>
    {x.approved_option&&<section className="approvedBanner">
      <span className="kicker light">{t('معتمد','Approved')}</span>
      <h2>{t('القرار معتمد','Decision approved')}: {t('الخيار','Option')} {x.approved_option}</h2>
      <p>{t('مسؤول التنفيذ','Decision owner')}: <b>{x.decision_owner}</b>{x.due_date&&<> &middot; {t('الموعد','Due')}: {x.due_date}</>}</p>
      <Link className="btn gold" href="/automate">{t('تنفيذ الإجراءات','Execute actions')}</Link>
    </section>}
    <div className="execBriefGrid">
      <section><h2>{t('لماذا؟','Why')}</h2><div className="briefCard"><L items={e.why}/></div></section>
      <section><h2>{t('ماذا أفعل الآن؟','What should I do now?')}</h2><div className="briefCard accent"><L items={e.next_actions}/></div></section>
      <section><h2>{t('أهم المخاطر','Top risks')}</h2><div className="briefCard"><L items={e.top_risks}/></div></section>
      <section><h2>{t('شروط القرار','Decision conditions')}</h2><div className="briefCard"><L items={e.decision_conditions}/></div></section>
    </div></>}
  </div></main>
}
