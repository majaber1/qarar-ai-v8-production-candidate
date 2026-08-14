'use client';

import {useLang} from './LanguageProvider';

const steps=[
  ['01','المشروع','Project'],['02','القرار','Decision'],['03','السياق','Context'],
  ['04','البدائل','Options'],['05','الأدلة','Evidence'],['06','التحليل','Analysis'],
  ['07','التوصية','Recommendation'],['08','الاعتماد','Approval'],['09','الإجراء','Action'],
];

export default function DecisionJourney({compact=false}:{compact?:boolean}){
  const{t}=useLang();
  return <div className={`decisionJourney ${compact?'compact':''}`} aria-label={t('رحلة القرار','Decision journey')}>
    {steps.map(([number,arabic,english],index)=><div className="journeyStep" key={number}>
      <span>{number}</span><b>{t(arabic,english)}</b>{index<steps.length-1&&<i aria-hidden="true">→</i>}
    </div>)}
  </div>;
}
