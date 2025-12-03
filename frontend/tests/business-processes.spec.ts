import { test, expect } from '@playwright/test';

test.describe('Business Processes CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/business-processes');
  });

  test('should create a new business process', async ({ page }) => {
    await page.click('text=Create New');
    await expect(page).toHaveURL(/\/dashboard\/business-processes\/new/);

    await page.fill('input[name="name"]', 'Test Process E2E');
    await page.fill('textarea[name="description"]', 'Created via Playwright test');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard\/business-processes/);
    await expect(page.locator('table')).toContainText('Test Process E2E');
  });

  test('should edit an existing business process', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'Test Process E2E' });
    await row.locator('a[href*="/edit"]').click();

    await expect(page).toHaveURL(/\/edit/);
    await page.fill('input[name="name"]', 'Test Process E2E Updated');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard\/business-processes/);
    await expect(page.locator('table')).toContainText('Test Process E2E Updated');
  });

  test('should delete a business process', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'Test Process E2E Updated' });
    await row.locator('button.text-destructive').click();

    await expect(page.locator('text=Are you absolutely sure?')).toBeVisible();
    await page.click('text=Delete');

    await expect(page.locator('table')).not.toContainText('Test Process E2E Updated');
  });
});
