/**
 * E2E Tests for Real-Time Status Updates
 * Story 4-2: Implement Real-Time Status Updates
 *
 * These tests verify that dashboard updates reflect database changes
 * within 1 minute via Supabase Realtime subscriptions.
 */

import { test, expect, Page } from "@playwright/test";
import { createClient, SupabaseClient } from "@supabase/supabase-js";
import { Database } from "../../lib/database.types";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || "";

let supabase: SupabaseClient<Database>;

test.beforeAll(() => {
  supabase = createClient<Database>(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
});

test.describe("E2E-4.3: Real-Time Dashboard Updates", () => {
  test.skip("should update dashboard within 1 minute when control status changes in database", async ({
    page,
  }) => {
    // Prerequisites: User must be logged in
    // This test is skipped until Story 4.1 dashboard is fully implemented
    await page.goto("/dashboard");

    // Wait for dashboard to load and Realtime to connect
    await expect(page.locator("text=Connected")).toBeVisible({ timeout: 10000 });

    // Note initial state
    const initialMetric = await page.locator('[data-testid="pending-reviews-count"]').textContent();

    // Simulate database change via Supabase service role
    const { data: insertedControl, error } = await supabase.from("controls").insert({
      name: "E2E Test Control",
      description: "Created by E2E test",
      status: "pending_review",
      tenant_id: "test-tenant-id", // Should match logged-in user's tenant
    }).select().single();

    expect(error).toBeNull();

    // Wait for dashboard to update (should be < 1 minute per AC-4.3)
    await expect(async () => {
      const updatedMetric = await page.locator('[data-testid="pending-reviews-count"]').textContent();
      expect(updatedMetric).not.toBe(initialMetric);
    }).toPass({ timeout: 60000 });

    // Cleanup
    if (insertedControl) {
      await supabase.from("controls").delete().eq("id", insertedControl.id);
    }
  });

  test.skip("should activate fallback polling when Realtime connection fails", async ({
    page,
  }) => {
    // Block Realtime WebSocket connection
    await page.route("**/realtime/**", (route) => route.abort());

    await page.goto("/dashboard");

    // Wait for connection to fail and fallback to activate
    await expect(page.locator("text=Disconnected")).toBeVisible({ timeout: 15000 });
    await expect(page.locator("text=Fallback polling is currently ACTIVE")).toBeVisible();

    // Verify dashboard still updates via polling (slower than Realtime)
    // Check that metrics query is being called periodically
    let queryCount = 0;
    page.on("request", (request) => {
      if (request.url().includes("/api/v1/dashboard/metrics")) {
        queryCount++;
      }
    });

    // Wait 65 seconds to capture at least one polling cycle (60s interval)
    await page.waitForTimeout(65000);

    expect(queryCount).toBeGreaterThanOrEqual(1);
  });

  test.skip("should change connection status indicator (connected → disconnected → reconnecting)", async ({
    page,
  }) => {
    await page.goto("/dashboard");

    // Initially should connect
    await expect(page.locator("text=Connected")).toBeVisible({ timeout: 10000 });

    // Simulate network disconnection
    await page.context().setOffline(true);

    // Status should change to disconnected
    await expect(page.locator("text=Disconnected")).toBeVisible({ timeout: 10000 });

    // Restore network
    await page.context().setOffline(false);

    // Status should reconnect
    await expect(page.locator("text=Connected")).toBeVisible({ timeout: 15000 });
  });
});

test.describe("E2E-4.3: Tenant Isolation", () => {
  test.skip("should NOT receive Realtime events from other tenants", async ({
    browser,
  }) => {
    // Create two browser contexts for two different tenants
    const tenantAContext = await browser.newContext();
    const tenantBContext = await browser.newContext();

    const tenantAPage = await tenantAContext.newPage();
    const tenantBPage = await tenantBContext.newPage();

    // Login as Tenant A user
    await loginAsTenant(tenantAPage, "tenant-a-user@example.com", "password123");
    await tenantAPage.goto("/dashboard");
    await expect(tenantAPage.locator("text=Connected")).toBeVisible({ timeout: 10000 });

    // Login as Tenant B user
    await loginAsTenant(tenantBPage, "tenant-b-user@example.com", "password123");
    await tenantBPage.goto("/dashboard");
    await expect(tenantBPage.locator("text=Connected")).toBeVisible({ timeout: 10000 });

    // Note Tenant A's initial state
    const tenantAInitialMetric = await tenantAPage
      .locator('[data-testid="dashboard-metrics"]')
      .textContent();

    // Insert control for Tenant B
    const { data: tenantBControl } = await supabase.from("controls").insert({
      name: "Tenant B Control",
      description: "Should NOT appear in Tenant A dashboard",
      status: "active",
      tenant_id: "tenant-b-id",
    }).select().single();

    // Wait 10 seconds (well within 1-minute Realtime SLA)
    await tenantBPage.waitForTimeout(10000);

    // Verify Tenant A's metrics did NOT change
    const tenantAUpdatedMetric = await tenantAPage
      .locator('[data-testid="dashboard-metrics"]')
      .textContent();
    expect(tenantAUpdatedMetric).toBe(tenantAInitialMetric);

    // Verify Tenant B's metrics DID change
    const tenantBUpdatedMetric = await tenantBPage
      .locator('[data-testid="dashboard-metrics"]')
      .textContent();
    expect(tenantBUpdatedMetric).not.toBe(tenantAInitialMetric);

    // Cleanup
    if (tenantBControl) {
      await supabase.from("controls").delete().eq("id", tenantBControl.id);
    }

    await tenantAContext.close();
    await tenantBContext.close();
  });
});

// Helper function for tenant-specific login
async function loginAsTenant(page: Page, email: string, password: string) {
  await page.goto("/login");
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/dashboard", { timeout: 10000 });
}
