'use client';

import Link from 'next/link';
import {useEffect,useMemo,useState} from 'react';
import {api,QCase} from '@/lib/api';
import {useLang} from './LanguageProvider';

type LoadState='loading'|'ready'|'error';

export default function CaseList({base,initialCases,externalState}:{base:string;initialCases?:QCase[];externalState?:LoadState}){
  const{t,status:statusLabel,urgency:urgencyLabel,locale}=useLang();
  const[cases,setCases]=useState<QCase[]>(initialCases||[]);
  const[state,setState]=useState<LoadState>(externalState||'loading');
  const[query,setQuery]=useState('');
  const[status,setStatus]=useState('all');

  useEffect(()=>{
    if(initialCases){setCases(initialCases);setState(externalState||'ready');return}
    let active=true;
    api.list().then(rows=>{if(active){setCases(rows);setState('ready')}}).catch(()=>{if(active)setState('error')});
    return()=>{active=false};
  },[initialCases,externalState]);

  const filtered=useMemo(()=>{
    const needle=query.trim().toLocaleLowerCase();
    return cases.filter(item=>(status==='all'||item.status===status)&&(!needle||`${item.title} ${item.description}`.toLocaleLowerCase().includes(needle)));
  },[cases,query,status]);
  const statuses=useMemo(()=>Array.from(new Set(cases.map(item=>item.status))),[cases]);

  return <div className="caseTable" aria-live="polite">
    <div className="caseToolbar"><label><span>⌕</span><input value={query} onChange={event=>setQuery(event.target.value)} placeholder={t('ابحث في الحالات...','Search decisions...')} aria-label={t('البحث في الحالات','Search decisions')}/></label><select value={status} onChange={event=>setStatus(event.target.value)} aria-label={t('تصفية حسب الحالة','Filter by status')}><option value="all">{t('كل الحالات','All statuses')}</option>{statuses.map(value=><option value={value} key={value}>{value.replaceAll('_',' ')}</option>)}</select></div>
    {state==='loading'&&<div className="tableMessage"><span className="loadingPulse"/><b>{t('جارٍ تحميل الحالات...','Loading decisions...')}</b></div>}
    {state==='error'&&<div className="inlineError"><b>{t('تعذر تحميل الحالات','Cases could not be loaded')}</b><span>{t('سجّل الدخول أو تأكد من اتصال خدمة قرار.','Sign in or check the Qarar service connection.')}</span><Link href="/login">{t('تسجيل الدخول','Sign in')} ←</Link></div>}
    {state==='ready'&&cases.length===0&&<div className="emptyCase"><b>{t('لا توجد حالات قرار بعد','No decision cases yet')}</b><span>{t('أنشئ أول حالة لتبدأ رحلة التحليل والاعتماد.','Create the first case to begin the analysis and approval journey.')}</span><Link href="/cases/new">＋ {t('حالة جديدة','New case')}</Link></div>}
    {state==='ready'&&cases.length>0&&filtered.length===0&&<div className="tableMessage"><b>{t('لا توجد نتائج مطابقة','No matching decisions')}</b><span>{t('جرّب عبارة بحث أو حالة مختلفة.','Try a different search or status.')}</span></div>}
    {filtered.length>0&&<div className="caseRows"><div className="caseTableHead"><span>{t('القرار','Decision')}</span><span>{t('الأولوية','Priority')}</span><span>{t('الحالة','Status')}</span><span>{t('آخر تحديث','Updated')}</span><span/></div>{filtered.map(item=><Link href={`${base}/${item.id}`} className="caseTableRow" key={item.id}><div><b>{item.title}</b><small>{item.description.replace(/^\[[^\]]+\]\s*/, '').slice(0,92)}</small></div><span className={`priorityBadge ${item.urgency}`}>{urgencyLabel(item.urgency)}</span><span className="statusBadge">{statusLabel(item.status)}</span><time dateTime={item.updated_at||item.created_at}>{new Intl.DateTimeFormat(locale,{month:'short',day:'numeric'}).format(new Date(item.updated_at||item.created_at))}</time><i className="directionalIcon">←</i></Link>)}</div>}
  </div>
}
