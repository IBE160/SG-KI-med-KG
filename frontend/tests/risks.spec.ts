import { test, expect } from '@playwright/test';

test.describe('Risks CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/risks');
  });

  test('should create a new risk', async ({ page }) => {
    await page.click('text=Create New');
    await expect(page).toHaveURL(/\/dashboard\/risks\/new/);

    await page.fill('input[name="name"]', 'Test Risk E2E');
    await page.fill('input[name="category"]', 'Financial');
    await page.fill('textarea[name="description"]', 'Created via Playwright test');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard\/risks/);
    await expect(page.locator('table')).toContainText('Test Risk E2E');
  });

  test('should edit an existing risk', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'Test Risk E2E' });
    await row.locator('a[href*="/edit"]').click();

    await expect(page).toHaveURL(/\/edit/);
    await page.fill('input[name="name"]', 'Test Risk E2E Updated');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard\/risks/);
    await expect(page.locator('table')).toContainText('Test Risk E2E Updated');
  });

  test('should delete a risk', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'Test Risk E2E Updated' });
    await row.locator('button.text-destructive').click();

    await expect(page.locator('text=Are you absolutely sure?')).toBeVisible();
    await page.click('text=Delete');

    await expect(page.locator('table')).not.toContainText('Test Risk E2E Updated');
  });
});
