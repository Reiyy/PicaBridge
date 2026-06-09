import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { md3 } from 'vuetify/blueprints'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import { zhHans } from 'vuetify/locale'

// 颜色
const appColors = {
  primary: '#496cc3',
  'primary-darken-1': '#3b5aa0',
  'primary-lighten-1': '#6b8fd6',
  secondary: '#5f6368',
  'secondary-darken-1': '#3c4043',
  surface: '#ffffff',
  'surface-bright': '#f8f9fa',
  'surface-variant': '#f1f3f4',
  background: '#f0f5fe',
  error: '#d93025',
  info: '#496cc3',
  success: '#1e8e3e',
  warning: '#f9ab00',
  'on-warning': '#ffffff',
  'on-primary': '#ffffff',
  'on-secondary': '#ffffff',
  'on-surface': '#202124',
  'on-surface-variant': '#5f6368',
  'on-background': '#202124',
}

export default createVuetify({
  blueprint: md3,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  locale: {
    locale: 'zhHans',
    messages: { zhHans },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: appColors,
        variables: {
          'border-color': '#dadce0',
          'border-opacity': 0.12,
          'high-emphasis-opacity': 0.87,
          'medium-emphasis-opacity': 0.6,
          'disabled-opacity': 0.38,
          'idle-opacity': 0.04,
          'hover-opacity': 0.04,
          'focus-opacity': 0.12,
          'selected-opacity': 0.08,
          'activated-opacity': 0.12,
          'pressed-opacity': 0.12,
          'dragged-opacity': 0.08,
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: '#8ab4f8',
          'primary-darken-1': '#669df6',
          secondary: '#9aa0a6',
          surface: '#1e1e1e',
          'surface-bright': '#2d2d2d',
          'surface-variant': '#353535',
          background: '#121212',
          error: '#f28b82',
          info: '#8ab4f8',
          success: '#81c995',
          warning: '#fdd663',
          'on-surface': '#e8eaed',
          'on-surface-variant': '#9aa0a6',
        },
      },
    },
  },
  defaults: {
    VBtn: {
      rounded: 'sm',
      elevation: 0,
      fontWeight: 500,
    },
    VCard: {
      rounded: 'lg',
      elevation: 0,
      border: true,
    },
    VTextField: {
      variant: 'filled',
      density: 'comfortable',
    },
    VSelect: {
      variant: 'filled',
      density: 'comfortable',
    },
    VAutocomplete: {
      variant: 'filled',
      density: 'comfortable',
    },
    VChip: {
      rounded: 'sm',
    },
    VSheet: {
      rounded: 'sm',
    },
    VDivider: {
      color: '#dadce0',
    },
    VList: {
      density: 'comfortable',
    },
    VListItem: {
      rounded: 'sm',
    },
    VTable: {
      density: 'comfortable',
    },
    VBadge: {
      rounded: 'pill',
    },
  },
})
