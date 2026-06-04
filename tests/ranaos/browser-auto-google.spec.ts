import { test, expect } from '@playwright/test';

test('browser automation - search snehal nautiyal', async ({ page }) => {
  await page.goto('https://duckduckgo.com');

  const searchBox = page.getByPlaceholder('Search privately');
  await searchBox.fill('Snehal Nautiyal');
  await searchBox.press('Enter');

  // Wait for results
  await page.waitForSelector('[data-testid="result"]', { timeout: 15000 });

  // Screenshot
  await page.screenshot({ path: 'tests/ranaos/search-snehal-result.png', fullPage: false });

  // Grab result text
  const results = await page.locator('[data-testid="result"]').allInnerTexts();
  console.log('--- SEARCH RESULTS ---');
  results.slice(0, 5).forEach((r, i) => console.log(`${i + 1}. ${r.slice(0, 200)}`));

  expect(results.length).toBeGreaterThan(0);
});
