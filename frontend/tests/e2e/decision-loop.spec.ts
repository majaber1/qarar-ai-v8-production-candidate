import {expect,test} from '@playwright/test';

const workspace=process.env.QARAR_E2E_WORKSPACE??'browser-tenant';
const email=process.env.QARAR_E2E_EMAIL??'executive@example.com';
const password=process.env.QARAR_E2E_PASSWORD??'browser-password-123';
const caseId=process.env.QARAR_E2E_CASE_ID??'1';

test('authenticated decision loop is bilingual, explainable, and responsive',async({page},testInfo)=>{
  await page.goto('/login');
  const textboxes=page.getByRole('textbox');
  await textboxes.nth(0).fill(workspace);
  await textboxes.nth(1).fill(email);
  await textboxes.nth(2).fill(password);
  await page.getByRole('button',{name:/Enter workspace|دخول (?:إلى )?المساحة/}).click();
  await expect(page).not.toHaveURL(/\/login$/);

  await page.goto(`/project/${caseId}`);
  await expect(page.getByText('deterministic-v2')).toBeVisible();
  await expect(page.getByRole('heading',{name:/What could change the recommendation|ما الذي قد يغيّر التوصية/})).toBeVisible();
  await expect(page.getByRole('heading',{name:/Turn the decision into action|حوّل التوصية إلى عمل/})).toBeVisible();

  if(testInfo.project.name.startsWith('mobile')){
    const menu=page.getByRole('button',{name:/Menu|القائمة/});
    await expect(menu).toBeVisible();
    await menu.click();
  }

  const initialDirection=await page.locator('html').getAttribute('dir');
  await page.getByRole('button',{name:/Switch to Arabic|التبديل إلى الإنجليزية/}).click();
  const expectedDirection=initialDirection==='rtl'?'ltr':'rtl';
  const expectedLanguage=expectedDirection==='rtl'?'ar':'en';
  await expect.poll(()=>page.locator('html').getAttribute('dir')).toBe(expectedDirection);
  await expect.poll(()=>page.locator('html').getAttribute('lang')).toBe(expectedLanguage);
  await expect(page.getByText(/Explainable confidence|ثقة قابلة للتفسير/)).toBeVisible();
});
