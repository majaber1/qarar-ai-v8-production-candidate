'use client';
import React,{createContext,useContext,useEffect,useState}from'react';
type Lang='ar'|'en';
const C=createContext<{lang:Lang;setLang:(x:Lang)=>void;t:(a:string,e:string)=>string}>({lang:'ar',setLang:()=>{},t:a=>a});
export function LanguageProvider({children}:{children:React.ReactNode}){const[lang,setLang0]=useState<Lang>('ar');useEffect(()=>{const s=(localStorage.getItem('qarar_lang') as Lang)||'ar';setLang0(s);document.documentElement.lang=s;document.documentElement.dir=s==='ar'?'rtl':'ltr'},[]);function setLang(x:Lang){setLang0(x);localStorage.setItem('qarar_lang',x);document.documentElement.lang=x;document.documentElement.dir=x==='ar'?'rtl':'ltr'}return <C.Provider value={{lang,setLang,t:(a,e)=>lang==='ar'?a:e}}>{children}</C.Provider>}
export const useLang=()=>useContext(C);
