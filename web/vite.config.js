import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  base: '/ui/',
  build: {
    outDir: './ui',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      '/pbapi': 'http://localhost:7777',
      '/auth': 'http://localhost:7777',
      '/assets': 'http://localhost:7777',
      '/comics': 'http://localhost:7777',
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/tokens";\n`,
      },
    },
  },
})
