import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { mdi } from 'vuetify/iconsets/mdi'

// 主題配置
const lightTheme = {
  dark: false,
  colors: {
    background: '#FFFFFF',
    surface: '#FFFFFF',
    'surface-bright': '#FFFFFF',
    'surface-light': '#EEEEEE',
    'surface-variant': '#424242',
    'on-surface-variant': '#EEEEEE',
    primary: '#1976D2',
    'primary-darken-1': '#1565C0',
    secondary: '#424242',
    'secondary-darken-1': '#1A1A1A',
    error: '#F44336',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FF9800',
    // 自定義顏色
    accent: '#82B1FF',
    'text-primary': '#212121',
    'text-secondary': '#757575',
    'card-background': '#FAFAFA',
    'sidebar-background': '#F5F5F5',
    'navbar-background': '#1976D2',
    'border-color': '#E0E0E0',
    'hover-color': '#F5F5F5',
  },
}

const darkTheme = {
  dark: true,
  colors: {
    background: '#121212',
    surface: '#212121',
    'surface-bright': '#ccbfd6',
    'surface-light': '#424242',
    'surface-variant': '#a3a3a3',
    'on-surface-variant': '#424242',
    primary: '#2196F3',
    'primary-darken-1': '#1976D2',
    secondary: '#54B6F2',
    'secondary-darken-1': '#48A999',
    error: '#FF5252',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
    // 自定義顏色
    accent: '#82B1FF',
    'text-primary': '#FFFFFF',
    'text-secondary': '#B0B0B0',
    'card-background': '#1E1E1E',
    'sidebar-background': '#1A1A1A',
    'navbar-background': '#1976D2',
    'border-color': '#404040',
    'hover-color': '#2A2A2A',
  },
}

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: lightTheme,
      dark: darkTheme,
    },
    variations: {
      colors: ['primary', 'secondary'],
      lighten: 4,
      darken: 4,
    },
  },
  defaults: {
    VCard: {
      flat: false,
      elevation: 2,
    },
    VBtn: {
      color: 'primary',
      style: 'text-transform: none;',
    },
    VTextField: {
      variant: 'outlined',
      color: 'primary',
    },
    VTextarea: {
      variant: 'outlined',
      color: 'primary',
    },
    VSelect: {
      variant: 'outlined',
      color: 'primary',
    },
    VAutocomplete: {
      variant: 'outlined',
      color: 'primary',
    },
    VCombobox: {
      variant: 'outlined',
      color: 'primary',
    },
    VFileInput: {
      variant: 'outlined',
      color: 'primary',
    },
    VAlert: {
      border: 'start',
      borderColor: 'primary',
    },
  },
})
