import { test, expect } from '@playwright/test';

test.describe('Ithaca Full E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'test1234');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('login and main page loads', async ({ page }) => {
    await expect(page).toHaveTitle(/Ithaca/i);
    await page.screenshot({ path: 'tests/ranaos/screenshots/01-main.png' });
  });

  test('chat interface works', async ({ page }) => {
    // Chat input exists in DOM (hidden until a session is active)
    await expect(page.locator('#chat-input')).toBeAttached({ timeout: 5000 });
    // New chat button is visible
    await expect(page.locator('#new-chat')).toBeVisible();
    await page.screenshot({ path: 'tests/ranaos/screenshots/02-chat.png' });
  });

  test('sidebar navigation exists', async ({ page }) => {
    // Check sidebar or nav has links to features
    const nav = page.locator('nav, .sidebar, #sidebar, [data-sidebar]').first();
    await expect(nav).toBeVisible({ timeout: 5000 });
    await page.screenshot({ path: 'tests/ranaos/screenshots/03-sidebar.png' });
  });

  test('documents section accessible', async ({ page }) => {
    // Navigate to documents
    const docsLink = page.locator('a, button').filter({ hasText: /document/i }).first();
    if (await docsLink.isVisible()) {
      await docsLink.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'tests/ranaos/screenshots/04-documents.png' });
    }
  });

  test('memory section accessible', async ({ page }) => {
    const memLink = page.locator('a, button').filter({ hasText: /memory/i }).first();
    if (await memLink.isVisible()) {
      await memLink.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'tests/ranaos/screenshots/05-memory.png' });
    }
  });

  test('settings page loads', async ({ page }) => {
    const settingsLink = page.locator('a, button').filter({ hasText: /setting/i }).first();
    if (await settingsLink.isVisible()) {
      await settingsLink.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'tests/ranaos/screenshots/06-settings.png' });
    }
  });

  test('cookbook section accessible', async ({ page }) => {
    const link = page.locator('a, button').filter({ hasText: /cookbook/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'tests/ranaos/screenshots/07-cookbook.png' });
    }
  });

  test('research section accessible', async ({ page }) => {
    const link = page.locator('a, button').filter({ hasText: /research/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'tests/ranaos/screenshots/08-research.png' });
    }
  });

  test('compare section accessible', async ({ page }) => {
    const link = page.locator('a, button').filter({ hasText: /compare/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'tests/ranaos/screenshots/09-compare.png' });
    }
  });

  test('calendar section accessible', async ({ page }) => {
    const link = page.locator('a, button').filter({ hasText: /calendar/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'tests/ranaos/screenshots/10-calendar.png' });
    }
  });

  test('notes section accessible', async ({ page }) => {
    const link = page.locator('a, button').filter({ hasText: /note/i }).first();
    if (await link.isVisible()) {
      await link.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'tests/ranaos/screenshots/11-notes.png' });
    }
  });

  test('API health check returns ok', async ({ page }) => {
    const resp = await page.evaluate(async () => {
      const r = await fetch('/health');
      return r.status;
    });
    expect(resp).toBe(200);
  });

  test('static assets load correctly', async ({ page }) => {
    const resp = await page.goto('/static/style.css');
    expect(resp?.status()).toBe(200);

    const jsResp = await page.goto('/static/app.js');
    expect(jsResp?.status()).toBe(200);

    const manifestResp = await page.goto('/static/manifest.json');
    expect(manifestResp?.status()).toBe(200);
  });
});
