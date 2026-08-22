import { expect, test } from '@playwright/test';

const workspace = process.env.QARAR_E2E_WORKSPACE ?? 'browser-tenant';
const email = process.env.QARAR_E2E_EMAIL ?? 'executive@example.com';
const password = process.env.QARAR_E2E_PASSWORD ?? 'browser-password-123';

test('creating a case with a normal description succeeds', async ({ page }) => {
  await page.goto('/login');
  const textboxes = page.getByRole('textbox');
  await textboxes.nth(0).fill(workspace);
  await textboxes.nth(1).fill(email);
  await textboxes.nth(2).fill(password);
  await page.getByRole('button', { name: /Enter workspace|دخول (?:إلى )?المساحة/ }).click();
  await expect(page).not.toHaveURL(/\/login$/);

  await page.goto('/cases/new');
  await page.locator('.decisionForm > .field > input').first().fill('Regression test: normal case title');
  await page.locator('.decisionForm > .field > textarea').first().fill('This is a normal, human-written description that does not start with a bracket character.');
  await page.locator('.decisionForm button[type="submit"], .decisionForm button.btn.primary').first().click();

  // Regression guard: a plain-language description must not be silently replaced with []
  // (which the backend rejects with 422, leaving the user stuck on /cases/new with an error banner).
  await expect(page).toHaveURL(/\/project\/\d+/, { timeout: 15000 });
  await expect(page.locator('.errorBox')).toHaveCount(0);
});
