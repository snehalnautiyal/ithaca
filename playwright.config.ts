import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/ranaos',
  timeout: 30_000,
  use: {
    baseURL: 'http://localhost:7860',
    headless: !!process.env.CI,
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
});
