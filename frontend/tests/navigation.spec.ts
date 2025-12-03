import { test, expect } from '@playwright/test';

test.describe('Data Management Navigation', () => {
  test('should navigate to Controls page', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('a[href="/dashboard/controls"]');
    await expect(page).toHaveURL(/\/dashboard\/controls/);
    await expect(page.locator('h1')).toContainText('Controls');
  });

  test('should navigate to Risks page', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('a[href="/dashboard/risks"]');
    await expect(page).toHaveURL(/\/dashboard\/risks/);
    await expect(page.locator('h1')).toContainText('Risks');
  });

  test('should navigate to Business Processes page', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('a[href="/dashboard/business-processes"]');
    await expect(page).toHaveURL(/\/dashboard\/business-processes/);
    await expect(page.locator('h1')).toContainText('Business Processes');
  });

  test('should navigate to Regulatory Frameworks page', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('a[href="/dashboard/regulatory-frameworks"]');
    await expect(page).toHaveURL(/\/dashboard\/regulatory-frameworks/);
    await expect(page.locator('h1')).toContainText('Regulatory Frameworks');
  });
});
