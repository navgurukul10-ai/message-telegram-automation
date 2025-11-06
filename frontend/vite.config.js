import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API to Flask backend running on 7000
      '/api': {
        target: 'http://localhost:7000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  preview: {
    port: 5173
  }
})


