'use client';

import Link from 'next/link';
import {useEffect,useMemo,useState} from 'react';
import CaseList from '@/components/CaseList';
import {api,QCase,QProject} from '@/lib/api';
import {useLang} from '@/components/LanguageProvider';

type LoadState='loading'|'ready'|'error';

const CLOSED_STATUSES=new Set(['approved','executed','archived','rejected']);

export default function OperatorDashboard(){
  const{t,status:statusLabel}=useLang();
  const[projects,setProjects]=useState<QProject[]>([]);
  const[cases,setCases]=useState<QCase[]>([]);
  const[state,setState]=useState<LoadState>('loading');

  useEffect(()=>{
    let active=true;
    Promise.all([api.projects(),api.list()])
      .then(([projectRows,caseRows])=>{if(active){setProjects(projectRows);setCases(caseRows);setState('ready')}})
      .catch(()=>{if(active)setState('error')});
    return()=>{active=false};
  },[]);

  const metrics=useMemo(()=>{
    const open=cases.filter(item=>!CLOSED_STATUSES.has(item.status)).length;
    const waiting=cases.filter(item=>item.status==='needs_clarification').length;
    const approval=cases.filter(item=>item.status==='recommendation_ready').length;
    const urgent=cases.filter(item=>['high','critical'].includes(item.urgency)&&!CLOSED_STATUSES.has(item.status)).length;
    const approved=cases.filter(item=>item.status==='approved'||item.status==='executed').length;
    return{open,waiting,approval,urgent,approved};
  },[cases]);

  const pipeline=[
    {label:t('مفتوحة','Open'),value:metrics.open,tone:'blue'},
    {label:t('بانتظار معلومات','Waiting for input'),value:metrics.waiting,tone:'amber'},
    {label:t('جاهزة للاعتماد','Ready for approval'),value:metrics.approval,tone:'violet'},
    {label:t('معتمدة','Approved'),value:metrics.approved,tone:'green'},
  ];
  const maxPipeline=Math.max(1,...pipeline.map(item=>item.value));
  const urgentCases=cases.filter(item=>['high','critical'].includes(item.urgency)&&!CLOSED_STATUSES.has(item.status)).slice(0,4);

  return <main className="dashboardPage">
    <section className="dashboardHero">
      <div className="container dashboardHeroInner">
        <div>
          <span className="dashboardEyebrow"><i/> {t('مركز قيادة القرارات','Decision command center')}</span>
          <h1>{t('حوّل العمل الجاري إلى قرارات واضحة.','Turn active work into clear decisions.')}</h1>
          <p>{t('صورة واحدة للمشاريع، الأدلة، الحالات التي تحتاج مدخلاتك، والقرارات الجاهزة للاعتماد.','One view for projects, evidence, cases needing input, and recommendations ready for approval.')}</p>
        </div>
        <div className="dashboardHeroActions">
          <Link className="btn primary" href="/cases/new">＋ {t('حالة قرار','Decision case')}</Link>
          <Link className="btn secondary" href="/projects/new">＋ {t('مشروع','Project')}</Link>
        </div>
      </div>
    </section>

    <section className="container dashboardCanvas">
      {state==='error'&&<div className="serviceBanner" role="status"><span>!</span><div><b>{t('الواجهة جاهزة، وخدمة البيانات غير متصلة','Dashboard ready; data service disconnected')}</b><p>{t('شغّل خدمة قرار أو حدّث QARAR_BACKEND_URL لعرض البيانات الحية.','Start the Qarar service or configure QARAR_BACKEND_URL to show live data.')}</p></div><Link href="/api/deployment-health">{t('فحص الاتصال','Check connection')} ↗</Link></div>}

      <div className="dashboardKpis" aria-busy={state==='loading'}>
        <article><span className="kpiIcon blue">◇</span><div><small>{t('المشاريع النشطة','Active projects')}</small><strong>{state==='loading'?'—':projects.filter(p=>p.status!=='archived').length}</strong><em>{t('مساحات عمل مرتبطة','connected workspaces')}</em></div></article>
        <article><span className="kpiIcon violet">◉</span><div><small>{t('الحالات المفتوحة','Open decisions')}</small><strong>{state==='loading'?'—':metrics.open}</strong><em>{t('قيد التحليل والمتابعة','in analysis and follow-up')}</em></div></article>
        <article><span className="kpiIcon amber">⌁</span><div><small>{t('تحتاج تدخلك','Need your input')}</small><strong>{state==='loading'?'—':metrics.waiting}</strong><em>{t('أسئلة أو أدلة ناقصة','questions or evidence missing')}</em></div></article>
        <article><span className="kpiIcon coral">!</span><div><small>{t('أولوية عالية','High priority')}</small><strong>{state==='loading'?'—':metrics.urgent}</strong><em>{t('تحتاج متابعة اليوم','need attention today')}</em></div></article>
      </div>

      <div className="dashboardLayout">
        <div className="dashboardPrimary">
          <section className="dashboardPanel pipelinePanel">
            <div className="panelHeading"><div><span className="kicker">{t('مسار القرار','Decision pipeline')}</span><h2>{t('أين يقف العمل الآن؟','Where does the work stand?')}</h2></div><Link href="/executive">{t('مكتب التنفيذي','Executive office')} ←</Link></div>
            <div className="pipelineBars">{pipeline.map(item=><div className="pipelineRow" key={item.label}><div><b>{item.label}</b><span>{item.value}</span></div><div className="pipelineTrack"><i className={item.tone} style={{width:`${Math.max(5,item.value/maxPipeline*100)}%`}}/></div></div>)}</div>
          </section>

          <section className="dashboardPanel caseQueuePanel">
            <div className="panelHeading"><div><span className="kicker">{t('قائمة العمل','Work queue')}</span><h2>{t('حالات القرار','Decision cases')}</h2></div><Link href="/cases/new">＋ {t('حالة جديدة','New case')}</Link></div>
            <CaseList base="/project" initialCases={state==='ready'?cases:undefined} externalState={state}/>
          </section>
        </div>

        <aside className="dashboardRail">
          <section className="dashboardPanel quickActionsPanel"><div className="panelHeading"><div><span className="kicker">{t('إجراء سريع','Quick action')}</span><h2>{t('ابدأ من هنا','Start here')}</h2></div></div><nav>
            <Link href="/projects/new"><span className="actionGlyph blue">＋</span><div><b>{t('أنشئ مشروعًا','Create project')}</b><small>{t('حدّد الهدف والمالك','Set objective and owner')}</small></div><i>←</i></Link>
            <Link href="/knowledge"><span className="actionGlyph violet">↑</span><div><b>{t('أضف الأدلة','Add evidence')}</b><small>{t('ملفات وسياسات وتقارير','Files, policies, reports')}</small></div><i>←</i></Link>
            <Link href="/cases/new"><span className="actionGlyph coral">◇</span><div><b>{t('افتح حالة قرار','Open decision case')}</b><small>{t('حلّل مشكلة أو خيارًا','Analyze a problem or option')}</small></div><i>←</i></Link>
          </nav></section>

          <section className="dashboardPanel attentionPanel"><div className="panelHeading"><div><span className="kicker">{t('يتطلب انتباهًا','Needs attention')}</span><h2>{t('أولوية اليوم','Today’s priority')}</h2></div></div>{urgentCases.length?urgentCases.map(item=><Link href={`/project/${item.id}`} key={item.id}><span className={`priorityDot ${item.urgency}`}/><div><b>{item.title}</b><small>{item.status.replaceAll('_',' ')}</small></div><i>←</i></Link>):<div className="railEmpty"><span>✓</span><b>{t('لا توجد حالات عاجلة','No urgent cases')}</b><small>{t('كل الأولويات تحت السيطرة.','All priorities are under control.')}</small></div>}</section>
        </aside>
      </div>

      <section className="dashboardPanel portfolioPanel">
        <div className="panelHeading"><div><span className="kicker">{t('محفظة العمل','Work portfolio')}</span><h2>{t('المشاريع','Projects')}</h2></div><Link href="/projects/new">{t('إضافة مشروع','Add project')} ←</Link></div>
        <div className="portfolioGrid">{projects.length?projects.slice(0,6).map(project=>{
          const related=cases.filter(item=>item.project_id===project.id);
          const completed=related.filter(item=>CLOSED_STATUSES.has(item.status)).length;
          const progress=related.length?Math.round(completed/related.length*100):0;
          return <Link href={`/project?project=${project.id}`} className="portfolioCard" key={project.id}><div className="portfolioTop"><span dir="ltr">Q{project.id}</span><i>{statusLabel(project.status)}</i></div><h3>{project.name}</h3><p>{project.objective}</p><div className="portfolioMeta"><span>{project.owner}</span><b>{related.length} {t('حالة','cases')}</b></div><div className="portfolioProgress" role="progressbar" aria-label={t('تقدم المشروع','Project progress')} aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}><i style={{width:`${progress}%`}}/></div></Link>
        }):<div className="portfolioEmpty"><span>◎</span><div><b>{t('محفظتك جاهزة لأول مشروع','Your portfolio is ready for its first project')}</b><p>{t('ابدأ بهدف واضح، ثم اربط به الأدلة وحالات القرار.','Start with a clear objective, then connect evidence and decision cases.')}</p></div><Link className="btn primary" href="/projects/new">＋ {t('إنشاء مشروع','Create project')}</Link></div>}</div>
      </section>
    </section>
  </main>
}
