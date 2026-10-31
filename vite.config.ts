import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  cacheDir: process.env.VITE_CACHE_DIR || 'node_modules/.vite',
  plugins: [react()],
  server: {
    watch: { ignored: ['**/data/**', '**/.venv/**', '**/.git/**'] },
    port: 5173,
    strictPort: true,
    proxy: { '/api': process.env.VITE_API_TARGET ?? 'http://127.0.0.1:8000' },
  },
})
