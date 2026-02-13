import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages uses '/security-dashboard/', Netlify uses '/'
const base = process.env.DEPLOY_TARGET === 'github' ? '/security-dashboard/' : '/'

export default defineConfig({
  plugins: [react()],
  base: base,
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
