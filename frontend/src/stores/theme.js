import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useTheme } from 'vuetify'

export const useThemeStore = defineStore('theme', () => {
  // 狀態
  const currentTheme = ref(localStorage.getItem('theme') || 'light')
  const systemPrefersDark = ref(window.matchMedia('(prefers-color-scheme: dark)').matches)
  const followSystemTheme = ref(
    localStorage.getItem('followSystemTheme') === null 
      ? false // 預設不跟隨系統主題，使用暗色方案
      : localStorage.getItem('followSystemTheme') === 'true'
  )

  // 計算屬性
  const isDark = computed(() => {
    if (followSystemTheme.value) {
      return systemPrefersDark.value
    }
    return currentTheme.value === 'dark'
  })

  const themeIcon = computed(() => {
    return isDark.value ? 'mdi-weather-night' : 'mdi-weather-sunny'
  })

  const themeText = computed(() => {
    return isDark.value ? '暗色模式' : '亮色模式'
  })

  // 動作
  const toggleTheme = () => {
    const newTheme = currentTheme.value === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
  }

  const setTheme = (theme) => {
    console.log('🎨 設定主題:', theme)
    currentTheme.value = theme
    followSystemTheme.value = false
    localStorage.setItem('theme', theme)
    localStorage.setItem('followSystemTheme', 'false')
    console.log('💾 保存主題到 localStorage:', theme)
    applyTheme()
  }

  const setFollowSystemTheme = (follow) => {
    followSystemTheme.value = follow
    localStorage.setItem('followSystemTheme', follow.toString())
    applyTheme()
  }

  const applyTheme = () => {
    const targetTheme = followSystemTheme.value 
      ? (systemPrefersDark.value ? 'dark' : 'light')
      : currentTheme.value

    console.log('🔄 應用主題:', targetTheme)

    // 更新 HTML 元素的 class 以支援 CSS 變數
    document.documentElement.classList.toggle('dark-theme', targetTheme === 'dark')
    document.documentElement.classList.toggle('light-theme', targetTheme === 'light')

    // 發出事件供 App.vue 監聽
    document.dispatchEvent(new CustomEvent('theme-changed', { 
      detail: { theme: targetTheme }
    }))
  }

  const initializeTheme = () => {
    console.log('🎨 初始化主題系統')

    // 載入已保存設定（若不存在則使用預設：不跟隨系統 + 淺色主題）
    const savedTheme = localStorage.getItem('theme')
    const savedFollow = localStorage.getItem('followSystemTheme')
    const savedScheme = localStorage.getItem('colorScheme')

    if (savedTheme) currentTheme.value = savedTheme
    if (savedFollow !== null) followSystemTheme.value = savedFollow === 'true'
    if (savedScheme && colorSchemes[savedScheme]) currentColorScheme.value = savedScheme

    // 監聽系統主題變化（僅在跟隨系統時生效）
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      systemPrefersDark.value = e.matches
      if (followSystemTheme.value) {
        applyTheme()
      }
    })

    // 套用主題與色彩方案
    applyTheme()
    updateVuetifyTheme(currentColorScheme.value)
  }

  // 預定義的主題色彩方案
  const colorSchemes = {
    default: {
      name: '預設藍色',
      light: {
        primary: '#1976D2',
        'primary-darken-1': '#1565C0',
        secondary: '#424242',
        'secondary-darken-1': '#1A1A1A',
        accent: '#82B1FF',
        'navbar-background': '#1976D2',
        info: '#2196F3',
      },
      dark: {
        primary: '#2196F3',
        'primary-darken-1': '#1976D2',
        secondary: '#54B6F2',
        'secondary-darken-1': '#48A999',
        accent: '#82B1FF',
        'navbar-background': '#2196F3',
        info: '#2196F3',
      }
    },
    purple: {
      name: '優雅紫色',
      light: {
        primary: '#673AB7',
        'primary-darken-1': '#512DA8',
        secondary: '#9C27B0',
        'secondary-darken-1': '#7B1FA2',
        accent: '#E1BEE7',
        'navbar-background': '#673AB7',
        info: '#9C27B0',
      },
      dark: {
        primary: '#9C27B0',
        'primary-darken-1': '#7B1FA2',
        secondary: '#E1BEE7',
        'secondary-darken-1': '#CE93D8',
        accent: '#BA68C8',
        'navbar-background': '#9C27B0',
        info: '#AB47BC',
      }
    },
    green: {
      name: '自然綠色',
      light: {
        primary: '#4CAF50',
        'primary-darken-1': '#388E3C',
        secondary: '#8BC34A',
        'secondary-darken-1': '#689F38',
        accent: '#A5D6A7',
        'navbar-background': '#4CAF50',
        info: '#66BB6A',
      },
      dark: {
        primary: '#66BB6A',
        'primary-darken-1': '#4CAF50',
        secondary: '#A5D6A7',
        'secondary-darken-1': '#81C784',
        accent: '#C8E6C9',
        'navbar-background': '#66BB6A',
        info: '#81C784',
      }
    },
    orange: {
      name: '活力橙色',
      light: {
        primary: '#FF9800',
        'primary-darken-1': '#F57C00',
        secondary: '#FFC107',
        'secondary-darken-1': '#FFA000',
        accent: '#FFD54F',
        'navbar-background': '#FF9800',
        info: '#FFB74D',
      },
      dark: {
        primary: '#FFB74D',
        'primary-darken-1': '#FF9800',
        secondary: '#FFD54F',
        'secondary-darken-1': '#FFCA28',
        accent: '#FFE082',
        'navbar-background': '#FFB74D',
        info: '#FFCC02',
      }
    },
    teal: {
      name: '清新青色',
      light: {
        primary: '#009688',
        'primary-darken-1': '#00796B',
        secondary: '#26A69A',
        'secondary-darken-1': '#00897B',
        accent: '#80CBC4',
        'navbar-background': '#009688',
        info: '#4DB6AC',
      },
      dark: {
        primary: '#4DB6AC',
        'primary-darken-1': '#26A69A',
        secondary: '#80CBC4',
        'secondary-darken-1': '#4DB6AC',
        accent: '#B2DFDB',
        'navbar-background': '#4DB6AC',
        info: '#80CBC4',
      }
    },
  }

  const currentColorScheme = ref(localStorage.getItem('colorScheme') || 'default')

  const setColorScheme = (schemeName) => {
    console.log('🌈 設定色彩方案:', schemeName)
    currentColorScheme.value = schemeName
    localStorage.setItem('colorScheme', schemeName)
    console.log('💾 保存色彩方案到 localStorage:', schemeName)
    
    // 延遲更新，確保 DOM 和 Vue 實例都已準備好
    setTimeout(() => {
      // 嘗試多種方式更新 Vuetify 主題
      updateVuetifyTheme(schemeName)
    }, 100)
    
    // 發出色彩方案變化事件
    document.dispatchEvent(new CustomEvent('color-scheme-changed', { 
      detail: { scheme: schemeName, colors: colorSchemes[schemeName] }
    }))
  }
  
  const updateVuetifyTheme = (schemeName) => {
    const colors = colorSchemes[schemeName]
    const lightColors = colors.light
    const darkColors = colors.dark
    
    console.log('🎨 嘗試更新 Vuetify 主題顏色:', schemeName)
    console.log('🎨 亮色顏色:', lightColors)
    console.log('🌙 暗色顏色:', darkColors)
    
    // 方法1: 通過 window.vuetifyTheme（僅更新允許鍵，且值必須為字串）
    if (typeof window !== 'undefined' && window.vuetifyTheme) {
      console.log('📱 方法1: 使用 window.vuetifyTheme')
      
      try {
        const lightTheme = window.vuetifyTheme.themes.value.light
        const darkTheme = window.vuetifyTheme.themes.value.dark

        const allowedKeys = new Set([
          'primary', 'primary-darken-1',
          'secondary', 'secondary-darken-1',
          'info', 'success', 'warning', 'error',
          'navbar-background', 'accent'
        ])

        ;['primary','primary-darken-1','secondary','secondary-darken-1','info','success','warning','error','navbar-background','accent'].forEach(key => {
          const lv = lightColors[key]
          const dv = darkColors[key]
          if (typeof lv === 'string' && allowedKeys.has(key)) {
            lightTheme.colors[key] = lv
          }
          if (typeof dv === 'string' && allowedKeys.has(key)) {
            darkTheme.colors[key] = dv
          }
        })
        
        // 強制重新渲染 - 通過切換主題
        const currentName = window.vuetifyTheme.global.name.value
        window.vuetifyTheme.global.name.value = currentName === 'light' ? 'dark' : 'light'
        setTimeout(() => {
          window.vuetifyTheme.global.name.value = currentName
        }, 10)
        
        console.log('✅ 方法1 更新完成')
      } catch (error) {
        console.error('❌ 方法1 失敗:', error)
      }
    }
    // 移除 CSS 變數直寫，避免與 Vuetify 顏色格式衝突
  }

  // 獲取當前色彩方案
  const getCurrentColors = computed(() => {
    const scheme = colorSchemes[currentColorScheme.value]
    return isDark.value ? scheme.dark : scheme.light
  })

  return {
    // 狀態
    currentTheme,
    systemPrefersDark,
    followSystemTheme,
    currentColorScheme,
    
    // 計算屬性
    isDark,
    themeIcon,
    themeText,
    getCurrentColors,
    
    // 動作
    toggleTheme,
    setTheme,
    setFollowSystemTheme,
    setColorScheme,
    updateVuetifyTheme,
    initializeTheme,
    
    // 數據
    colorSchemes,
  }
})
