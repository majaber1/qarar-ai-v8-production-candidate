'use client';
import Link from 'next/link';
import {usePathname} from 'next/navigation';
import {useLang} from './LanguageProvider';

export default function AppHeader(){
  const{lang,setLang,t}=useLang();const path=usePathname();
  const links=[['/project',t('لوحة القيادة','Dashboard')],['/executive',t('مكتب التنفيذي','Executive office')],['/knowledge',t('المعرفة','Knowledge')],['/developer',t('التشغيل','Operations')]];
  return <header className="top"><div className="topin">
    <Link className="brand" href="/"><span className="mark">ق</span><div><b>{t('قرار','QARAR')}</b><small>{t('وضوح يقود إلى قرار','Clarity that leads to action')}</small></div></Link>
    <nav className="nav" aria-label={t('التنقل الرئيسي','Main navigation')}>{links.map(([href,label])=><Link className={path.startsWith(href)?'active':''} href={href} key={href}>{label}</Link>)}</nav>
    <div className="headerActions"><button className="langBtn" onClick={()=>setLang(lang==='ar'?'en':'ar')}>{lang==='ar'?'English':'العربية'}</button><Link className="loginLink" href="/profile">{t('حسابي','My account')}</Link><Link className="navCta" href="/cases/new">{t('حالة قرار جديدة','New decision case')}</Link></div>
  </div></header>
}
