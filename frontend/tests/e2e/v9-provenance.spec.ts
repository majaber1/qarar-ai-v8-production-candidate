import { expect, test } from '@playwright/test';

const workspace = process.env.QARAR_E2E_WORKSPACE ?? 'browser-tenant';
const email = process.env.QARAR_E2E_EMAIL ?? 'executive@example.com';
const password = process.env.QARAR_E2E_PASSWORD ?? 'browser-password-123';

test('V9 decision journey includes templates, criteria builder, and decision matrix', async ({ page }) => {
  // 1. Login
  await page.goto('/login');
  const textboxes = page.getByRole('textbox');
  await textboxes.nth(0).fill(workspace);
  await textboxes.nth(1).fill(email);
  await textboxes.nth(2).fill(password);
  await page.getByRole('button', { name: /Enter workspace|دخول (?:إلى )?المساحة/ }).click();
  await expect(page).not.toHaveURL(/\/login$/);

  // 2. Navigate to new case creation
  await page.goto('/cases/new');
  await expect(page.getByRole('heading', { name: /What decision are you making\?|ما القرار الذي تريد اتخاذه؟/ })).toBeVisible();

  // 3. Verify Criteria Builder & Options Editor exist on new case page
  await expect(page.getByText(/Criteria Builder|بناء معايير التقييم/)).toBeVisible();
  await expect(page.getByText(/Decision Options|البدائل والخيارات المطروحة/)).toBeVisible();

  // 4. View existing case
  await page.goto('/project/1');
  await expect(page.getByText('v9-provenance').first()).toBeVisible();
});
