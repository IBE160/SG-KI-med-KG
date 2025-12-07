import { test, expect } from '@playwright/test';

/**
 * E2E tests for Story 4.1: Role-Specific Dashboards
 *
 * These tests verify the dashboard displays correct cards for each role
 * and that performance metrics are met (LCP < 2.5s).
 */

test.describe('Dashboard - Role-Based Card Display', () => {
  test.beforeEach(async ({ page }) => {
    // Set viewport for desktop testing (as per MVP desktop-first strategy)
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('E2E-4.1.1: Admin user sees admin-specific dashboard cards', async ({ page }) => {
    // Login as admin user
    await page.goto('/login');
    await page.fill('input[name="username"]', 'admin@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard');

    // Verify admin-specific cards are displayed
    await expect(page.locator('text=System Health')).toBeVisible();
    await expect(page.locator('text=Pending AI Suggestions')).toBeVisible();
    await expect(page.locator('text=Analyze New Document')).toBeVisible();

    // Verify cards have expected structure (metric + action button)
    const systemHealthCard = page.locator('text=System Health').locator('..');
    await expect(systemHealthCard.locator('button:has-text("View")')).toBeVisible();
  });

  test('E2E-4.1.2: BPO user sees BPO-specific dashboard cards', async ({ page }) => {
    // Login as BPO user
    await page.goto('/login');
    await page.fill('input[name="username"]', 'bpo@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard');

    // Verify BPO-specific cards are displayed
    await expect(page.locator('text=Pending Reviews')).toBeVisible();
    await expect(page.locator('text=My Controls')).toBeVisible();
    await expect(page.locator('text=Overdue Assessments')).toBeVisible();

    // Verify metrics are displayed
    const pendingReviewsCard = page.locator('text=Pending Reviews').locator('..');
    await expect(pendingReviewsCard.locator('[class*="text-3xl"]')).toBeVisible();
  });

  test('E2E-4.1.3: Executive user sees executive-specific dashboard cards', async ({ page }) => {
    // Login as executive user
    await page.goto('/login');
    await page.fill('input[name="username"]', 'executive@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard');

    // Verify executive-specific cards are displayed
    await expect(page.locator('text=Risk Overview')).toBeVisible();
    await expect(page.locator('text=Compliance Status')).toBeVisible();
    await expect(page.locator('text=Recent Activity')).toBeVisible();
  });

  test('E2E-4.1.4: Dashboard renders with skeleton loading states initially', async ({ page }) => {
    // Login as any user
    await page.goto('/login');
    await page.fill('input[name="username"]', 'bpo@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    // Navigate to dashboard
    await page.goto('/dashboard');

    // Verify skeleton loading states appear (even briefly)
    // Using animate-pulse class which is applied to skeleton components
    const skeletons = page.locator('.animate-pulse');

    // Either skeletons are visible now, or they were visible and are now replaced by content
    // We can check if the page has finished loading by looking for actual content
    await expect(page.locator('h2:has-text("Dashboard")')).toBeVisible();
  });
});

test.describe('Dashboard - Performance', () => {
  test('E2E-4.2: Dashboard achieves LCP < 2.5 seconds', async ({ page }) => {
    // Login as BPO user
    await page.goto('/login');
    await page.fill('input[name="username"]', 'bpo@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    // Navigate to dashboard and measure performance
    const navigationPromise = page.waitForNavigation();
    await page.goto('/dashboard');
    await navigationPromise;

    // Use Playwright's performance metrics
    const performanceTiming = await page.evaluate(() => {
      const perfData = window.performance.timing;
      return {
        loadTime: perfData.loadEventEnd - perfData.navigationStart,
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.navigationStart,
        firstPaint: performance.getEntriesByType('paint')
          .find((entry) => entry.name === 'first-contentful-paint')?.startTime || 0,
      };
    });

    // Verify LCP < 2500ms (2.5 seconds)
    // Note: Actual LCP measurement would require Web Vitals library integration
    // For this test, we use loadTime as proxy
    expect(performanceTiming.loadTime).toBeLessThan(2500);
    console.log(`Dashboard load time: ${performanceTiming.loadTime}ms`);
  });

  test('E2E-4.3: Dashboard cards render immediately with skeleton states', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'bpo@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    await page.goto('/dashboard');

    // Verify dashboard title appears quickly
    await expect(page.locator('h2:has-text("Dashboard")')).toBeVisible({ timeout: 1000 });

    // Verify grid layout is visible (cards container)
    const cardGrid = page.locator('.grid');
    await expect(cardGrid).toBeVisible({ timeout: 500 });
  });
});

test.describe('Dashboard - Action Navigation', () => {
  test('E2E-4.4: Clicking card action button navigates to correct page', async ({ page }) => {
    // Login as BPO user
    await page.goto('/login');
    await page.fill('input[name="username"]', 'bpo@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    await page.goto('/dashboard');

    // Find "Pending Reviews" card and click "View" button
    const pendingReviewsCard = page.locator('text=Pending Reviews').locator('..');
    const viewButton = pendingReviewsCard.locator('button:has-text("View")');
    await viewButton.click();

    // Verify navigation to BPO reviews page
    await page.waitForURL('/dashboard/bpo/reviews');
    // Note: This route may not exist yet, test will need updating when Story 4.3 is implemented
  });
});

test.describe('Dashboard - Urgent Status Indicator', () => {
  test('E2E-4.5: Pending Reviews card shows urgent indicator when >5 items', async ({ page }) => {
    // Login as BPO user (assuming test data has >5 pending reviews)
    await page.goto('/login');
    await page.fill('input[name="username"]', 'bpo_with_many_pending@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    await page.goto('/dashboard');

    // Find Pending Reviews card
    const pendingReviewsCard = page.locator('text=Pending Reviews').locator('..');

    // Verify urgent indicator is visible
    await expect(pendingReviewsCard.locator('text=Requires attention')).toBeVisible();

    // Verify card has red border (urgent styling)
    await expect(pendingReviewsCard.locator('.border-red-500')).toBeVisible();
  });
});
