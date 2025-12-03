import { test, expect } from '@playwright/test';

test.describe('Controls CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/controls');
  });

  test('should create a new control', async ({ page }) => {
    await page.click('text=Create New');
    await expect(page).toHaveURL(/\/dashboard\/controls\/new/);

    await page.fill('input[name="name"]', 'Test Control E2E');
    await page.fill('input[name="type"]', 'Preventive');
    await page.fill('textarea[name="description"]', 'Created via Playwright test');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard\/controls/);
    await expect(page.locator('table')).toContainText('Test Control E2E');
  });

  test('should edit an existing control', async ({ page }) => {
    // Assuming 'Test Control E2E' exists from previous test
    const row = page.locator('tr', { hasText: 'Test Control E2E' });
    await row.locator('a[href*="/edit"]').click();

    await expect(page).toHaveURL(/\/edit/);
    await page.fill('input[name="name"]', 'Test Control E2E Updated');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard\/controls/);
    await expect(page.locator('table')).toContainText('Test Control E2E Updated');
  });

  test('should delete a control', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'Test Control E2E Updated' });
    await row.locator('button.text-destructive').click();

    await expect(page.locator('text=Are you absolutely sure?')).toBeVisible();
    await page.click('text=Delete');

    await expect(page.locator('table')).not.toContainText('Test Control E2E Updated');
  });
});
