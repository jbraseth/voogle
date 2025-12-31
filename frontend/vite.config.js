import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import sveltePreprocess from 'svelte-preprocess'

// Detect if running inside Docker (backend hostname resolves) or natively
// In Docker: backend service is at http://backend:80
// Native dev: backend is at http://localhost:8080
const BACKEND_TARGET = process.env.VITE_BACKEND_TARGET || 'http://localhost:8080'

export default defineConfig({
  plugins: [
    svelte({
      preprocess: [sveltePreprocess({ postcss: true })],
    }),
  ],
  server: {
    host: '0.0.0.0',
    proxy: {
      // Proxy API requests to backend - avoids CORS/PNA issues in dev
      '/api': {
        target: BACKEND_TARGET,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // Proxy local media files to backend
      '/local': {
        target: BACKEND_TARGET,
        changeOrigin: true,
      },
    },
  },
})
