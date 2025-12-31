import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import sveltePreprocess from 'svelte-preprocess'

export default defineConfig({
  plugins: [
    svelte({
      preprocess: [sveltePreprocess({ postcss: true })],
    }),
  ],
  server: {
    proxy: {
      // Proxy API requests to backend - avoids CORS/PNA issues in dev
      '/api': {
        target: 'http://backend:80',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // Proxy local media files to backend
      '/local': {
        target: 'http://backend:80',
        changeOrigin: true,
      },
    },
  },
})
