import { computed } from 'vue'
import { useTheme as useVuetifyTheme } from 'vuetify'
import { useThemeStore } from '@/stores/theme'

/**
 * 主題組合式函數
 * 提供便利的主題相關功能
 */
export function useTheme() {
  const vuetifyTheme = useVuetifyTheme()
  const themeStore = useThemeStore()

  // 計算屬性
  const isDark = computed(() => themeStore.isDark)
  const currentTheme = computed(() => themeStore.currentTheme)
  const themeColors = computed(() => vuetifyTheme.current.value.colors)
  const primaryColor = computed(() => themeColors.value.primary)
  const secondaryColor = computed(() => themeColors.value.secondary)

  // 主題相關的CSS類
  const themeClasses = computed(() => ({
    'dark-theme': isDark.value,
    'light-theme': !isDark.value,
  }))

  // 動態樣式生成器
  const getThemeStyle = (property, colorName, opacity = 1) => {
    const color = themeColors.value[colorName]
    if (!color) return {}
    
    return {
      [property]: `rgb(${color} / ${opacity})`
    }
  }

  // 獲取主題色的RGB值
  const getRgbColor = (colorName) => {
    return themeColors.value[colorName] || '0, 0, 0'
  }

  // 生成漸變背景
  const createGradient = (color1, color2, direction = '45deg') => {
    const rgb1 = getRgbColor(color1)
    const rgb2 = getRgbColor(color2)
    return `linear-gradient(${direction}, rgb(${rgb1}), rgb(${rgb2}))`
  }

  // 生成陰影樣式
  const createShadow = (size = 'medium', color = 'primary', opacity = 0.1) => {
    const shadowSizes = {
      small: '0 2px 4px',
      medium: '0 4px 8px',
      large: '0 8px 16px',
      extra: '0 12px 24px'
    }
    
    const shadowBase = shadowSizes[size] || shadowSizes.medium
    const rgb = getRgbColor(color)
    return `${shadowBase} rgba(${rgb}, ${opacity})`
  }

  // 獲取對比色文本
  const getContrastText = (backgroundColorName) => {
    // 簡單的對比度檢查，實際應用中可能需要更複雜的計算
    const darkColors = ['primary-darken-1', 'secondary-darken-1', 'error', 'warning']
    return darkColors.includes(backgroundColorName) ? 'white' : 'black'
  }

  // 主題動畫配置
  const themeTransition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
  const hoverTransition = 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'

  // 響應式斷點
  const breakpoints = {
    xs: '(max-width: 599px)',
    sm: '(min-width: 600px) and (max-width: 959px)',
    md: '(min-width: 960px) and (max-width: 1263px)',
    lg: '(min-width: 1264px) and (max-width: 1903px)',
    xl: '(min-width: 1904px)',
  }

  // 常用的主題樣式組合
  const getCardStyle = (variant = 'default') => {
    const variants = {
      default: {
        backgroundColor: `rgb(${getRgbColor('surface')})`,
        boxShadow: createShadow('medium', 'primary', 0.08),
        border: `1px solid rgb(${getRgbColor('border-color')} / 0.12)`,
        borderRadius: '12px',
        transition: themeTransition,
      },
      elevated: {
        backgroundColor: `rgb(${getRgbColor('surface')})`,
        boxShadow: createShadow('large', 'primary', 0.12),
        borderRadius: '16px',
        transition: themeTransition,
      },
      flat: {
        backgroundColor: `rgb(${getRgbColor('surface')})`,
        border: `1px solid rgb(${getRgbColor('border-color')} / 0.12)`,
        borderRadius: '8px',
        transition: themeTransition,
      },
      glass: {
        backgroundColor: `rgb(${getRgbColor('surface')} / 0.8)`,
        backdropFilter: 'blur(10px)',
        border: `1px solid rgb(${getRgbColor('primary')} / 0.2)`,
        borderRadius: '12px',
        transition: themeTransition,
      }
    }

    return variants[variant] || variants.default
  }

  const getButtonStyle = (variant = 'default') => {
    const variants = {
      default: {
        backgroundColor: `rgb(${getRgbColor('primary')})`,
        color: getContrastText('primary'),
        borderRadius: '8px',
        fontWeight: '500',
        textTransform: 'none',
        transition: hoverTransition,
      },
      outlined: {
        backgroundColor: 'transparent',
        color: `rgb(${getRgbColor('primary')})`,
        border: `2px solid rgb(${getRgbColor('primary')})`,
        borderRadius: '8px',
        fontWeight: '500',
        textTransform: 'none',
        transition: hoverTransition,
      },
      text: {
        backgroundColor: 'transparent',
        color: `rgb(${getRgbColor('primary')})`,
        borderRadius: '8px',
        fontWeight: '500',
        textTransform: 'none',
        transition: hoverTransition,
      }
    }

    return variants[variant] || variants.default
  }

  return {
    // 狀態
    isDark,
    currentTheme,
    themeColors,
    primaryColor,
    secondaryColor,
    themeClasses,

    // Store 方法
    toggleTheme: themeStore.toggleTheme,
    setTheme: themeStore.setTheme,
    setColorScheme: themeStore.setColorScheme,

    // 工具函數
    getThemeStyle,
    getRgbColor,
    createGradient,
    createShadow,
    getContrastText,
    getCardStyle,
    getButtonStyle,

    // 常量
    themeTransition,
    hoverTransition,
    breakpoints,
  }
}
