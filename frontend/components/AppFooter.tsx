'use client';

import{useLang}from'./LanguageProvider';

export default function AppFooter(){
  const{t}=useLang();
  return <footer><div><b>{t('قرار','QARAR')}</b><span>{t('منصة قرار مؤسسية مبنية للسوق العربي.','An enterprise decision platform built for the Arab market.')}</span></div><small>{t('الإنسان يعتمد القرار، والذكاء الاصطناعي يوضّح الصورة.','People approve the decision; AI clarifies the picture.')}</small></footer>;
}
