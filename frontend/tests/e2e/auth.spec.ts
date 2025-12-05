import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should navigate to register page', async ({ page }) => {
    await page.goto('/login');
    await page.click('text=Sign up');
    await expect(page).toHaveURL('/register');
    await expect(page.locator('h3')).toContainText('Sign Up');
  });

  test('should show validation errors on empty registration submit', async ({ page }) => {
    await page.goto('/register');
    await page.click('button[type="submit"]');
    // Expect HTML5 validation or text content if novalidate
    // Since we used Shadcn Form which uses react-hook-form, it might not submit but show errors
    // We need to check if error messages appear.
    // Our schema requires valid email.
    await expect(page.locator('text=Please enter a valid email address')).toBeVisible();
    await expect(page.locator('text=Password must be at least 8 characters')).toBeVisible();
  });

  test('should navigate between login and register', async ({ page }) => {
    await page.goto('/register');
    await page.click('text=Back to login');
    await expect(page).toHaveURL('/login');
  });
});
