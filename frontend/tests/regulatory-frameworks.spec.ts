import { test, expect } from '@playwright/test';

test.describe('Regulatory Frameworks CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/regulatory-frameworks');
  });

  test('should create a new regulatory framework', async ({ page }) => {
    await page.click('text=Create New');
    await expect(page).toHaveURL(/\/dashboard\/regulatory-frameworks\/new/);

    await page.fill('input[name="name"]', 'Test Framework E2E');
    await page.fill('input[name="version"]', '1.0');
    await page.fill('textarea[name="description"]', 'Created via Playwright test');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard\/regulatory-frameworks/);
    await expect(page.locator('table')).toContainText('Test Framework E2E');
  });

  test('should edit an existing regulatory framework', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'Test Framework E2E' });
    await row.locator('a[href*="/edit"]').click();

    await expect(page).toHaveURL(/\/edit/);
    await page.fill('input[name="name"]', 'Test Framework E2E Updated');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard\/regulatory-frameworks/);
    await expect(page.locator('table')).toContainText('Test Framework E2E Updated');
  });

  test('should delete a regulatory framework', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'Test Framework E2E Updated' });
    await row.locator('button.text-destructive').click();

    await expect(page.locator('text=Are you absolutely sure?')).toBeVisible();
    await page.click('text=Delete');

    await expect(page.locator('table')).not.toContainText('Test Framework E2E Updated');
  });
});
