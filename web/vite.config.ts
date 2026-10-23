import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [react()],
  cacheDir: '../.cache/vite',
  server: {
    proxy: {
      '/api': `http://127.0.0.1:${process.env.API_PORT || 8000}`,
      '/docs': `http://127.0.0.1:${process.env.API_PORT || 8000}`,
      '/openapi.json': `http://127.0.0.1:${process.env.API_PORT || 8000}`,
    },
  },
  test: { environment: 'jsdom', setupFiles: ['./src/__tests__/setup.ts'], css: false },
});
