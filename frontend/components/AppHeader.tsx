'use client';

import Link from 'next/link';
import{usePathname}from'next/navigation';
import{useEffect,useState}from'react';
import{useLang}from'./LanguageProvider';

export default function AppHeader(){
  const{lang,setLang,t}=useLang();
  const path=usePathname();
  const[open,setOpen]=useState(false);
  const links=[
    ['/project',t('لوحة القيادة','Dashboard')],
    ['/executive',t('مكتب التنفيذي','Executive office')],
    ['/knowledge',t('المعرفة','Knowledge')],
    ['/developer',t('التشغيل','Operations')],
  ];

  useEffect(()=>setOpen(false),[path]);

  return <>
    <a className="skipLink" href="#main-content">{t('تجاوز إلى المحتوى','Skip to content')}</a>
    <header className="top"><div className="topin">
      <Link className="brand" href="/" aria-label={t('قرار — الصفحة الرئيسية','Qarar — home')}><span className="mark" aria-hidden="true">ق</span><div><b>{t('قرار','QARAR')}</b><small>{t('وضوح يقود إلى قرار','Clarity that leads to action')}</small></div></Link>
      <button className="menuButton" type="button" aria-expanded={open} aria-controls="primary-navigation" onClick={()=>setOpen(value=>!value)}><span aria-hidden="true">{open?'×':'☰'}</span>{t('القائمة','Menu')}</button>
      <nav id="primary-navigation" className={`nav ${open?'open':''}`} aria-label={t('التنقل الرئيسي','Main navigation')}>{links.map(([href,label])=><Link aria-current={path.startsWith(href)?'page':undefined} className={path.startsWith(href)?'active':''} href={href} key={href}>{label}</Link>)}</nav>
      <div className={`headerActions ${open?'open':''}`}><button className="langBtn" type="button" aria-label={t('التبديل إلى الإنجليزية','Switch to Arabic')} onClick={()=>setLang(lang==='ar'?'en':'ar')}>{lang==='ar'?'English':'العربية'}</button><Link className="loginLink" href="/profile">{t('حسابي','My account')}</Link><Link className="navCta" href="/cases/new">{t('حالة قرار جديدة','New decision case')}</Link></div>
    </div></header>
  </>;
}
