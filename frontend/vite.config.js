import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    https: {
      key: './certs/key.pem',
      cert: './certs/cert.pem'
    },
    port: 8443,
    host: true
  },
  preview: {
    https: {
      key: './certs/key.pem',
      cert: './certs/cert.pem'
    },
    port: 8443,
    host: true
  }
})
