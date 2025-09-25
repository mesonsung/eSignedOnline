<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
      elevation="2"
    >
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      
      <v-toolbar-title class="text-h5 font-weight-bold">
        eSignedOnline
      </v-toolbar-title>
      
      <v-spacer></v-spacer>
      
      <!-- 語言選擇 -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
            class="mr-2"
          >
            <v-icon>mdi-translate</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item
            v-for="lang in supportedLanguages"
            :key="lang.code"
            @click="changeLanguage(lang.code)"
            :class="{ 'v-list-item--active': currentLanguage === lang.code }"
          >
            <v-list-item-title>{{ lang.name }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      
      <!-- 用戶選單 -->
      <v-menu v-if="isAuthenticated">
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
          >
            <v-icon>mdi-account-circle</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item>
            <v-list-item-title>{{ $t('user.profile') }}</v-list-item-title>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="logout">
            <v-list-item-title>{{ $t('auth.logout') }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-navigation-drawer
      v-model="drawer"
      app
      temporary
    >
      <v-list>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          :disabled="item.disabled"
        >
          <template v-slot:prepend>
            <v-icon>{{ item.icon }}</v-icon>
          </template>
          <v-list-item-title>{{ $t(item.title) }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <router-view />
    </v-main>

    <!-- 全域通知 -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="snackbar.show = false"
        >
          {{ $t('common.close') }}
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const authStore = useAuthStore()
const { locale } = useI18n()

const drawer = ref(false)

const isAuthenticated = computed(() => authStore.isAuthenticated)

const currentLanguage = computed(() => locale.value)

const supportedLanguages = [
  { code: 'zh-TW', name: '繁體中文' },
  { code: 'en', name: 'English' },
  { code: 'vi', name: 'Tiếng Việt' }
]

const menuItems = computed(() => {
  const items = []
  
  if (!isAuthenticated.value) {
    items.push(
      { title: 'auth.login', icon: 'mdi-login', to: '/login' },
      { title: 'auth.register', icon: 'mdi-account-plus', to: '/register' }
    )
  } else {
    items.push(
      { title: 'nav.dashboard', icon: 'mdi-view-dashboard', to: '/dashboard' },
      { title: 'nav.documents', icon: 'mdi-file-document', to: '/documents' }
    )
    
    if (authStore.user?.role === 'admin') {
      items.push(
        { title: 'nav.upload', icon: 'mdi-upload', to: '/upload' },
        { title: 'nav.users', icon: 'mdi-account-group', to: '/users' }
      )
    }
    
    items.push(
      { title: 'nav.my-signed', icon: 'mdi-file-sign', to: '/my-signed' }
    )
  }
  
  return items
})

const snackbar = ref({
  show: false,
  message: '',
  color: 'success',
  timeout: 3000
})

const changeLanguage = (langCode) => {
  locale.value = langCode
  localStorage.setItem('language', langCode)
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  // 載入保存的語言設定
  const savedLanguage = localStorage.getItem('language')
  if (savedLanguage && supportedLanguages.some(lang => lang.code === savedLanguage)) {
    locale.value = savedLanguage
  }
})
</script>

<style scoped>
.v-list-item--active {
  background-color: rgba(25, 118, 210, 0.12);
}
</style>
