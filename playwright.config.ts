import { defineConfig } from '@playwright/test'
import path from 'node:path'

const python = path.resolve(
  process.platform === 'win32'
    ? '.venv/Scripts/python.exe'
    : '.venv/bin/python',
)
const apiPort = process.env.UI_TEST_API_PORT || '18175'
const uiPort = process.env.UI_TEST_PORT || '15175'
export default defineConfig({
  testDir: './tests/browser',
  fullyParallel: false,
  workers: 1,
  timeout: 90000,
  expect: { timeout: 15000 },
  reporter: 'list',
  use: {
    actionTimeout: 15000,
    baseURL: `http://127.0.0.1:${uiPort}`,
    channel:
      process.env.PLAYWRIGHT_CHANNEL ??
      (process.platform === 'win32' ? 'msedge' : undefined),
    headless: true,
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: '"' + python + '" scripts/browser-test-server.py',
      url: `http://127.0.0.1:${apiPort}/api/health`,
      env: { UI_TEST_API_PORT: apiPort },
      reuseExistingServer: false,
      timeout: 30000,
    },
    {
      command: `node node_modules/vite/bin/vite.js --host 127.0.0.1 --port ${uiPort} --strictPort`,
      url: `http://127.0.0.1:${uiPort}`,
      env: {
        VITE_API_TARGET: `http://127.0.0.1:${apiPort}`,
        VITE_CACHE_DIR: 'node_modules/.vite-ui-tests',
      },
      reuseExistingServer: false,
      timeout: 30000,
    },
  ],
})
