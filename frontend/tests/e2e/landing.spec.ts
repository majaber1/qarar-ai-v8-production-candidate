import {expect,test} from '@playwright/test';

test.beforeEach(async({page},testInfo)=>{
  const language=testInfo.project.name.endsWith('-ar')?'ar':'en';
  await page.addInitScript((value)=>localStorage.setItem('qarar_lang',value),language);
});

test('landing page explains the product and the complete decision journey',async({page},testInfo)=>{
  const arabic=testInfo.project.name.endsWith('-ar');
  await page.goto('/',{waitUntil:'domcontentloaded'});
  await expect(page.locator('html')).toHaveAttribute('lang',arabic?'ar':'en');
  await expect(page.getByRole('heading',{name:arabic?'قرار يساعدك على تحويل القرارات المعقدة إلى قرارات قابلة للتفسير والتنفيذ.':'Qarar helps you turn complex decisions into explainable, actionable decisions.'})).toBeVisible();
  await expect(page.getByRole('link',{name:arabic?'ابدأ قرارًا جديدًا':'Start a New Decision'})).toHaveAttribute('href','/cases/new');
  await expect(page.getByRole('link',{name:arabic?'استعرض مشروعًا قائمًا':'Open Existing Project'})).toHaveAttribute('href','/project');
  await expect(page.getByText(arabic?'التوصية':'Recommendation',{exact:true})).toBeVisible();
  await expect(page.getByText(arabic?'حالة القرار':'Decision Case',{exact:true})).toBeVisible();
  expect(await page.evaluate(()=>document.body.getBoundingClientRect().width<=window.innerWidth)).toBeTruthy();
});
