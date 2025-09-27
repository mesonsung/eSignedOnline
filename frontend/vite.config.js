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
  build: {
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('vuetify')) return 'vendor-vuetify'
            if (id.includes('vue')) return 'vendor-vue'
            if (id.includes('vue-router')) return 'vendor-vue-router'
            if (id.includes('pinia')) return 'vendor-pinia'
            if (id.includes('pdf-lib')) return 'vendor-pdf'
            return 'vendor'
          }
        }
      }
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
