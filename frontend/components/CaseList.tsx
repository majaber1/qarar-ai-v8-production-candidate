"use client";
import Link from "next/link";
import {useEffect,useState} from "react";
import {api,QCase} from "@/lib/api";
import {useLang} from "./LanguageProvider";

export default function CaseList({base}:{base:string}){
  const{t}=useLang();
  const[cases,setCases]=useState<QCase[]>([]);
  const[state,setState]=useState<'loading'|'ready'|'error'>('loading');
  useEffect(()=>{api.list().then(x=>{setCases(x);setState('ready')}).catch(()=>setState('error'))},[]);
  return <div className="card caseList" aria-live="polite">
    {state==='loading'&&<p className="muted">{t('جارٍ تحميل الحالات...','Loading cases...')}</p>}
    {state==='error'&&<div className="inlineError"><b>{t('تعذر تحميل الحالات','Cases could not be loaded')}</b><span>{t('سجّل الدخول أو تأكد من اتصال خدمة قرار.','Sign in or check the Qarar service connection.')}</span><Link href="/login">{t('تسجيل الدخول','Sign in')} ←</Link></div>}
    {state==='ready'&&cases.length===0&&<div className="emptyCase"><b>{t('لا توجد حالات قرار بعد','No decision cases yet')}</b><span>{t('أنشئ أول حالة لتبدأ رحلة التحليل والاعتماد.','Create the first case to begin the analysis and approval journey.')}</span><Link href="/cases/new">＋ {t('حالة جديدة','New case')}</Link></div>}
    {cases.map(x=><Link href={`${base}/${x.id}`} className="case" key={x.id}><div><b>{x.title}</b><div className="muted">{x.description.replace(/^\[[^\]]+\]\s*/, '').slice(0,100)}</div></div><span className="badge">{x.urgency}</span><span className="badge gold">{x.status}</span></Link>)}
  </div>
}
