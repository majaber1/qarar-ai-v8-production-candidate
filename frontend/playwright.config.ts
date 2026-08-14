import {defineConfig,devices} from '@playwright/test';

export default defineConfig({
  testDir:'./tests/e2e',
  timeout:30_000,
  fullyParallel:true,
  workers:process.env.CI?1:2,
  forbidOnly:!!process.env.CI,
  retries:process.env.CI?2:0,
  reporter:'list',
  use:{baseURL:process.env.QARAR_E2E_BASE_URL??'http://127.0.0.1:3123',trace:'retain-on-failure'},
  webServer:process.env.QARAR_E2E_BASE_URL?undefined:{command:'npm run start -- -p 3123',url:'http://127.0.0.1:3123',reuseExistingServer:!process.env.CI,timeout:120_000},
  projects:[
    {name:'desktop-en',use:{...devices['Desktop Chrome']}},
    {name:'desktop-ar',use:{...devices['Desktop Chrome']}},
    {name:'mobile-en',use:{...devices['Pixel 7']}},
    {name:'mobile-ar',use:{...devices['Pixel 7']}},
  ],
});
