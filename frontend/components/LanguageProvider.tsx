'use client';

import React,{createContext,useContext,useEffect,useMemo,useState} from 'react';

export type Lang='ar'|'en';

type LanguageContextValue={
  lang:Lang;
  setLang:(language:Lang)=>void;
  t:(arabic:string,english:string)=>string;
  status:(value:string)=>string;
  urgency:(value:string)=>string;
  locale:string;
};

const STATUS_LABELS:Record<string,[string,string]>={
  draft:['مسودة','Draft'],
  open:['مفتوحة','Open'],
  analyzing:['قيد التحليل','Analyzing'],
  needs_clarification:['بانتظار معلومات','Waiting for input'],
  recommendation_ready:['جاهزة للاعتماد','Ready for approval'],
  approved:['معتمدة','Approved'],
  executed:['نُفذت','Executed'],
  failed:['فشلت','Failed'],
  rejected:['مرفوضة','Rejected'],
  archived:['مؤرشفة','Archived'],
  active:['نشط','Active'],
  pending:['قيد الانتظار','Pending'],
};

const URGENCY_LABELS:Record<string,[string,string]>={
  low:['منخفضة','Low'],
  medium:['متوسطة','Medium'],
  high:['عالية','High'],
  critical:['حرجة','Critical'],
};

const LanguageContext=createContext<LanguageContextValue>({
  lang:'ar',setLang:()=>{},t:arabic=>arabic,status:value=>value,urgency:value=>value,locale:'ar-SA',
});

export function LanguageProvider({children}:{children:React.ReactNode}){
  const[lang,setLangState]=useState<Lang>('ar');

  useEffect(()=>{
    const stored=localStorage.getItem('qarar_lang');
    const initial:Lang=stored==='en'?'en':'ar';
    setLangState(initial);
    document.documentElement.lang=initial;
    document.documentElement.dir=initial==='ar'?'rtl':'ltr';
  },[]);

  const value=useMemo<LanguageContextValue>(()=>({
    lang,
    setLang(language){
      setLangState(language);
      localStorage.setItem('qarar_lang',language);
      document.documentElement.lang=language;
      document.documentElement.dir=language==='ar'?'rtl':'ltr';
    },
    t:(arabic,english)=>lang==='ar'?arabic:english,
    status(value){const labels=STATUS_LABELS[value];return labels?labels[lang==='ar'?0:1]:value.replaceAll('_',' ')},
    urgency(value){const labels=URGENCY_LABELS[value];return labels?labels[lang==='ar'?0:1]:value},
    locale:lang==='ar'?'ar-SA':'en-US',
  }),[lang]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export const useLang=()=>useContext(LanguageContext);
