<template>
  <v-app>
    <v-app-bar
      app
      color="navbar-background"
      elevation="2"
      class="app-bar"
    >
      <v-app-bar-nav-icon color="white" class="hamburger-btn" @click="drawer = !drawer"></v-app-bar-nav-icon>
      
      <v-toolbar-title class="text-h5 font-weight-bold text-white">
        eSignedOnline
      </v-toolbar-title>
      
      <v-spacer></v-spacer>
      
      <!-- 主題切換 -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
            class="mr-2"
            color="white"
          >
            <v-icon>{{ themeStore.themeIcon }}</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="themeStore.toggleTheme()">
            <template v-slot:prepend>
              <v-icon>{{ themeStore.isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
            </template>
            <v-list-item-title>
              {{ themeStore.isDark ? $t('theme.switchToLight') : $t('theme.switchToDark') }}
            </v-list-item-title>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="showThemeDialog = true">
            <template v-slot:prepend>
              <v-icon>mdi-palette</v-icon>
            </template>
            <v-list-item-title>{{ $t('theme.customize') }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      
      <!-- 語言選擇 -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
            class="mr-2"
            color="white"
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
            color="white"
          >
            <v-icon>mdi-account-circle</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="$router.push('/profile')">
            <template v-slot:prepend>
              <v-icon>mdi-account</v-icon>
            </template>
            <v-list-item-title>{{ $t('user.profile') }}</v-list-item-title>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="logout">
            <template v-slot:prepend>
              <v-icon>mdi-logout</v-icon>
            </template>
            <v-list-item-title>{{ $t('auth.logout') }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-navigation-drawer
      v-model="drawer"
      app
      temporary
      color="sidebar-background"
      class="sidebar"
    >
      <v-list nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          :disabled="item.disabled"
          class="sidebar-item"
          color="primary"
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

    <!-- 主題定制對話框 -->
    <v-dialog
      v-model="showThemeDialog"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="text-h5 d-flex align-center">
          <v-icon class="mr-3">mdi-palette</v-icon>
          {{ $t('theme.customize') }}
        </v-card-title>
        
        <v-card-text>
          <!-- 主題模式選擇 -->
          <v-list>
            <v-list-subheader>{{ $t('theme.mode') }}</v-list-subheader>
            <v-radio-group 
              :model-value="themeStore.followSystemTheme ? 'system' : themeStore.currentTheme"
              @update:model-value="(value) => {
                if (value === 'system') {
                  themeStore.setFollowSystemTheme(true)
                } else {
                  themeStore.setFollowSystemTheme(false)
                  themeStore.setTheme(value)
                }
              }"
              hide-details
            >
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-brightness-auto</v-icon>
                </template>
                <v-list-item-title>{{ $t('theme.followSystem') }}</v-list-item-title>
                <template v-slot:append>
                  <v-radio value="system" color="primary"></v-radio>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-weather-sunny</v-icon>
                </template>
                <v-list-item-title>{{ $t('theme.light') }}</v-list-item-title>
                <template v-slot:append>
                  <v-radio value="light" color="primary"></v-radio>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-weather-night</v-icon>
                </template>
                <v-list-item-title>
                  {{ $t('theme.dark') }}
                  <v-chip size="small" color="primary" variant="tonal" class="ml-2">
                    {{ $t('theme.default') }}
                  </v-chip>
                </v-list-item-title>
                <template v-slot:append>
                  <v-radio value="dark" color="primary"></v-radio>
                </template>
              </v-list-item>
            </v-radio-group>
          </v-list>
          
          <v-divider class="my-4"></v-divider>
          
          <!-- 色彩方案選擇 -->
          <div>
            <v-list-subheader>{{ $t('theme.colorScheme') }}</v-list-subheader>
            
            <div
              v-for="(scheme, key) in themeStore.colorSchemes"
              :key="key"
              class="d-flex align-center pa-3 ma-1 rounded cursor-pointer"
              :class="{ 
                'bg-primary': themeStore.currentColorScheme === key,
                'text-white': themeStore.currentColorScheme === key,
                'elevation-2': themeStore.currentColorScheme === key 
              }"
              @click="themeStore.setColorScheme(key)"
            >
              <v-avatar size="28" class="mr-3">
                <div class="color-preview" :style="{
                  background: `linear-gradient(45deg, ${scheme.light.primary}, ${scheme.light.secondary})`
                }"></div>
              </v-avatar>
              <div class="flex-grow-1 font-weight-medium">{{ scheme.name }}</div>
              <v-icon 
                v-if="themeStore.currentColorScheme === key"
                color="white"
                size="20"
              >
                mdi-check
              </v-icon>
            </div>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            variant="text"
            @click="showThemeDialog = false"
          >
            {{ $t('common.close') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useI18n } from 'vue-i18n'
import { useTheme } from 'vuetify'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const theme = useTheme()
const { locale } = useI18n()

// 將 Vuetify 主題實例暴露給全域，讓 store 能直接訪問
window.vuetifyTheme = theme

// 響應式變數
const showThemeDialog = ref(false)

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
  
  // 初始化主題系統
  themeStore.initializeTheme()
  
  // 立即應用保存的主題設置
  const savedTheme = themeStore.followSystemTheme 
    ? (themeStore.systemPrefersDark ? 'dark' : 'light')
    : themeStore.currentTheme
  console.log('🎯 App.vue 應用主題:', savedTheme)
  theme.global.name.value = savedTheme
  console.log('✅ Vuetify 主題已設置為:', theme.global.name.value)
  
  // 監聽主題變化事件
  document.addEventListener('theme-changed', (event) => {
    console.log('🔄 收到主題變化事件:', event.detail.theme)
    theme.global.name.value = event.detail.theme
    console.log('✅ Vuetify 主題已更新為:', theme.global.name.value)
  })
  
  // 色彩方案的應用與監聽統一由 themeStore 管理
  
  // 監聽全域通知事件
  window.addEventListener('show-snackbar', (event) => {
    snackbar.value = {
      show: true,
      message: event.detail.message,
      color: event.detail.color,
      timeout: event.detail.timeout || 3000
    }
  })
})
</script>

<style scoped>
.hamburger-btn {
  background-color: rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.hamburger-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.v-list-item--active {
  background-color: rgba(25, 118, 210, 0.12);
}

.app-bar {
  transition: background-color 0.3s ease;
}

.sidebar {
  transition: background-color 0.3s ease;
}

.sidebar-item {
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.sidebar-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
  transform: translateX(4px);
}

.color-preview {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

/* 主題相關的全域樣式變數 */
:global(.v-application) {
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 卡片陰影動畫 */
:global(.v-card) {
  transition: all 0.2s ease;
}

:global(.v-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

/* 按鈕動畫 */
:global(.v-btn) {
  transition: all 0.2s ease;
}

:global(.v-btn:hover) {
  transform: translateY(-1px);
}

/* 深色主題特定樣式 */
:global(.dark-theme .v-card:hover) {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
}

/* 亮色主題特定樣式 */
:global(.light-theme .v-card) {
  background-color: rgb(var(--v-theme-card-background));
}

/* 響應式設計 */
@media (max-width: 960px) {
  .app-bar .text-h5 {
    font-size: 1.25rem !important;
  }
}

@media (max-width: 600px) {
  .sidebar-item {
    margin: 2px 4px;
  }
}

/* 平滑滾動 */
:global(html) {
  scroll-behavior: smooth;
}

/* 自定義滾動條 */
/* 色彩方案選擇器樣式 */
.cursor-pointer {
  cursor: pointer;
  transition: all 0.2s ease;
}

.cursor-pointer:hover {
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
}

:global(::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:global(::-webkit-scrollbar-track) {
  background: rgba(var(--v-theme-surface-variant), 0.1);
  border-radius: 4px;
}

:global(::-webkit-scrollbar-thumb) {
  background: rgba(var(--v-theme-primary), 0.3);
  border-radius: 4px;
  transition: background 0.2s ease;
}

:global(::-webkit-scrollbar-thumb:hover) {
  background: rgba(var(--v-theme-primary), 0.5);
}

/* 暗色主題滾動條 */
:global(.dark-theme ::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.1);
}

:global(.dark-theme ::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.2);
}

:global(.dark-theme ::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.3);
}
</style>
