'use client';
import {FormEvent,useState} from 'react';
import {useRouter} from 'next/navigation';
import {useLang} from '@/components/LanguageProvider';
export default function Login(){
 const r=useRouter(),{t}=useLang();const[busy,setBusy]=useState(false),[err,setErr]=useState('');
 async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();setBusy(true);setErr('');const f=new FormData(e.currentTarget);const key=String(f.get('key')||'');const res=await fetch('/api/session/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key})});if(!res.ok){setErr(t('بيانات الدخول غير صحيحة','Invalid credentials'));setBusy(false);return;}r.push('/');r.refresh();}
 return <main className="container"><section className="decisionForm" style={{maxWidth:640,margin:'60px auto'}}><span className="kicker">SECURE ACCESS</span><h1>{t('الدخول إلى Qarar','Sign in to Qarar')}</h1><p className="muted">{t('في V8 أصبحت واجهات REST وMCP محمية ومربوطة بالمستأجر والصلاحيات.','V8 protects REST and MCP surfaces with tenant-scoped identities and roles.')}</p><form onSubmit={submit}><div className="field"><label>{t('مفتاح الوصول','Access key')}</label><input name="key" type="password" autoComplete="current-password" required/></div>{err&&<div className="errorBox">{err}</div>}<button className="btn gold" disabled={busy}>{busy?t('جارٍ التحقق...','Signing in...'):t('دخول','Sign in')}</button></form></section></main>
}
