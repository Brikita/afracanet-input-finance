import { defineConfig } from '@playwright/test'
import path from 'node:path'

const python = path.resolve(
  process.platform === 'win32'
    ? '.venv/Scripts/python.exe'
    : '.venv/bin/python',
)
export default defineConfig({
  testDir: './tests/connected-browser',
  workers: 1,
  timeout: 120000,
  expect: { timeout: 20000 },
  reporter: 'list',
  use: {
    channel: process.platform === 'win32' ? 'msedge' : undefined,
    headless: true,
    actionTimeout: 20000,
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: `"${python}" scripts/connected/browser_servers.py`,
      url: 'http://127.0.0.1:18001/api/health',
      reuseExistingServer: false,
      timeout: 45000,
    },
    {
      command:
        'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 15173 --strictPort',
      url: 'http://127.0.0.1:15173',
      env: {
        VITE_API_TARGET: 'http://127.0.0.1:18000',
        VITE_CREDIT_WORKSPACE_URL: 'http://127.0.0.1:15174/',
        VITE_CACHE_DIR: 'node_modules/.vite-connected',
      },
      reuseExistingServer: false,
    },
    {
      command:
        'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 15174 --strictPort',
      cwd: path.resolve('../afracanet-green-path'),
      url: 'http://127.0.0.1:15174',
      env: {
        VITE_CREDIT_API_URL: 'http://127.0.0.1:18001',
        VITE_CACHE_DIR: 'node_modules/.vite-connected',
        VITE_INPUT_FINANCE_URL: 'http://127.0.0.1:15173/',
      },
      reuseExistingServer: false,
      timeout: 45000,
    },
  ],
})
