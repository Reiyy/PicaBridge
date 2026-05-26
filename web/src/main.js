import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { zhHans } from 'vuetify/locale'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

import App from './App.vue'
import router from './router'
import { generateThemeFromColor, loadThemeConfig, DEFAULT_SOURCE_COLOR } from './utils/theme'

// 从 localStorage 读取已保存的 Monet 配置，或使用默认颜色
const savedConfig = loadThemeConfig()
const initialSourceColor = savedConfig?.sourceColor || DEFAULT_SOURCE_COLOR
const initialTheme = generateThemeFromColor(initialSourceColor)

const vuetify = createVuetify({
  components,
  directives,
  locale: {
    locale: 'zhHans',
    messages: { zhHans },
  },
  theme: {
    defaultTheme: savedConfig?.darkMode ? 'dark' : 'light',
    themes: {
      light: {
        dark: false,
        colors: initialTheme.light,
      },
      dark: {
        dark: true,
        colors: initialTheme.dark,
      },
    },
  },
})

createApp(App)
  .use(createPinia())
  .use(router)
  .use(vuetify)
  .mount('#app')
