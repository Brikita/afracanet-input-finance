import { defineConfig } from '@playwright/test'
import path from 'node:path'

const python = path.resolve(
  process.platform === 'win32'
    ? '.venv/Scripts/python.exe'
    : '.venv/bin/python',
)
export default defineConfig({
  testDir: './tests/browser',
  fullyParallel: false,
  workers: 1,
  timeout: 90000,
  expect: { timeout: 15000 },
  reporter: 'list',
  use: {
    actionTimeout: 15000,
    baseURL: 'http://127.0.0.1:5174',
    channel:
      process.env.PLAYWRIGHT_CHANNEL ??
      (process.platform === 'win32' ? 'msedge' : undefined),
    headless: true,
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: '"' + python + '" scripts/browser-test-server.py',
      url: 'http://127.0.0.1:8001/api/health',
      reuseExistingServer: false,
      timeout: 30000,
    },
    {
      command: 'npx vite --host 127.0.0.1 --port 5174',
      url: 'http://127.0.0.1:5174',
      env: { VITE_API_TARGET: 'http://127.0.0.1:8001' },
      reuseExistingServer: false,
      timeout: 30000,
    },
  ],
})
