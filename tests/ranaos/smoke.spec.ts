import { test, expect } from '@playwright/test';

test('ithaca loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Ithaca/i);
});
