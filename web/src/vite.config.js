import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
  ],
  base: '/ui/',
  build: {
    outDir: '../ui',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      '/pbapi': 'http://localhost:7777',
      '/auth': 'http://localhost:7777',
      '/assets': 'http://localhost:7777',
    },
  },
})
