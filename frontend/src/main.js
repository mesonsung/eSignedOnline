import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import i18n from './plugins/i18n'
import './assets/styles/theme.css'

// Pre-apply theme before app mount to avoid FOUC on first paint (e.g., login page)
try {
  const followSystem = localStorage.getItem('followSystemTheme') === 'true'
  const savedTheme = localStorage.getItem('theme') || 'light'
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const targetTheme = followSystem ? (systemPrefersDark ? 'dark' : 'light') : savedTheme

  document.documentElement.classList.toggle('dark-theme', targetTheme === 'dark')
  document.documentElement.classList.toggle('light-theme', targetTheme === 'light')

  // Set Vuetify theme name early
  if (vuetify?.theme?.global?.name) {
    vuetify.theme.global.name.value = targetTheme
  }
} catch (_) {
  // no-op
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(i18n)

app.mount('#app')
