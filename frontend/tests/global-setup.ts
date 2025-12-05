import { chromium, FullConfig } from "@playwright/test";

async function globalSetup(config: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Go to login page
  await page.goto(config.projects[0].use.baseURL + "/login");

  // Fill login form
  await page.fill('input[name="username"]', "admin@example.com");
  await page.fill('input[name="password"]', "Admin123!");
  await page.click('button[type="submit"]');

  // Wait for navigation to dashboard
  await page.waitForURL(/\/dashboard/);

  // Save signed-in state to 'storageState.json'
  await page.context().storageState({ path: "storageState.json" });

  await browser.close();
}

export default globalSetup;
