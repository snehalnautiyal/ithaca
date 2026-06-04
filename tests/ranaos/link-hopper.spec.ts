import { test } from '@playwright/test';

test('hop 50 links starting from DuckDuckGo search', async ({ page }) => {
  test.setTimeout(600000); // 10 min timeout

  await page.goto('https://duckduckgo.com');
  const searchBox = page.getByPlaceholder('Search privately');
  await searchBox.fill('interesting websites');
  await searchBox.press('Enter');
  await page.waitForSelector('[data-testid="result"]', { timeout: 15000 });

  // Click first search result
  await page.locator('[data-testid="result"] a').first().click();
  await page.waitForLoadState('domcontentloaded');
  console.log(`Page 1: ${page.url()}`);
  await page.waitForTimeout(10000);

  for (let i = 2; i <= 50; i++) {
    try {
      const link = page.locator('a[href^="http"]').first();
      await link.click({ timeout: 5000 });
      await page.waitForLoadState('domcontentloaded');
      console.log(`Page ${i}: ${page.url()}`);
      await page.waitForTimeout(10000);
    } catch {
      console.log(`Page ${i}: no clickable link found, going back`);
      await page.goBack();
      await page.waitForTimeout(2000);
      // Try a different link
      const links = page.locator('a[href^="http"]');
      const count = await links.count();
      if (count > 1) {
        await links.nth(1).click({ timeout: 5000 });
        await page.waitForLoadState('domcontentloaded');
        console.log(`Page ${i} (retry): ${page.url()}`);
        await page.waitForTimeout(10000);
      }
    }
  }

  await page.screenshot({ path: 'tests/ranaos/link-hopper-final.png' });
  console.log('Done — visited 50 pages');
});
