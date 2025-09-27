# eSignedOnline 主題系統

這個主題系統提供了完整的亮色/暗色主題支援，以及多種色彩方案選擇。

## 功能特色

### 🎨 主題模式
- **亮色主題** - 現代化的明亮界面
- **暗色主題** - 舒適的深色界面  
- **跟隨系統** - 自動跟隨系統主題設定

### 🌈 色彩方案
- **預設藍色** - 專業的藍色主題
- **優雅紫色** - 典雅的紫色主題
- **自然綠色** - 清新的綠色主題
- **活力橙色** - 充滿活力的橙色主題
- **清新青色** - 寧靜的青色主題

### ✨ 設計元素
- 流暢的動畫過渡效果
- 統一的圓角和陰影設計
- 響應式設計支援
- 自定義滾動條樣式
- 懸停動畫效果

## 使用方法

### 在組件中使用主題

#### 1. 使用組合式函數
```vue
<script setup>
import { useTheme } from '@/composables/useTheme'

const { 
  isDark, 
  primaryColor, 
  createGradient,
  getCardStyle 
} = useTheme()
</script>
```

#### 2. 使用主題 Store
```vue
<script setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

// 切換主題
themeStore.toggleTheme()

// 設定特定主題
themeStore.setTheme('dark')

// 設定色彩方案
themeStore.setColorScheme('purple')
</script>
```

#### 3. 使用 CSS 類
```vue
<template>
  <div class="themed-card hover-lift">
    <h1 class="text-gradient">標題</h1>
    <p class="fade-enter-active">內容</p>
  </div>
</template>
```

### CSS 變數

系統提供了豐富的 CSS 變數：

```css
/* 動畫 */
var(--theme-transition)
var(--hover-transition)

/* 圓角 */
var(--border-radius-sm)
var(--border-radius-md) 
var(--border-radius-lg)
var(--border-radius-xl)

/* 陰影 */
var(--shadow-light)
var(--shadow-medium)
var(--shadow-heavy)

/* 間距 */
var(--spacing-xs) 到 var(--spacing-xxl)

/* 顏色 */
var(--text-primary)
var(--text-secondary)
var(--surface-1)
var(--surface-2)
var(--border-color)
```

### 工具類

```css
/* 動畫類 */
.fade-enter-active
.slide-up-enter-active
.scale-enter-active

/* 效果類 */
.text-gradient
.glass-effect
.hover-lift
.hover-scale

/* 組件類 */
.themed-card
.themed-button
.themed-input
```

## 自定義主題

### 添加新的色彩方案

在 `stores/theme.js` 中添加：

```javascript
const colorSchemes = {
  // ... 現有方案
  myCustom: {
    name: '我的自定義',
    light: {
      primary: '#YOUR_COLOR',
      secondary: '#YOUR_SECONDARY',
    },
    dark: {
      primary: '#YOUR_DARK_PRIMARY',
      secondary: '#YOUR_DARK_SECONDARY', 
    }
  }
}
```

### 修改 Vuetify 主題

在 `plugins/vuetify.js` 中修改：

```javascript
const lightTheme = {
  dark: false,
  colors: {
    // 添加或修改顏色
    'my-custom-color': '#FF6B6B',
  }
}
```

## 響應式設計

主題系統完全支援響應式設計：

```css
@media (max-width: 960px) {
  /* 平板樣式 */
}

@media (max-width: 600px) {
  /* 手機樣式 */
}
```

## 可訪問性

- 支援 `prefers-reduced-motion` 
- 支援 `prefers-contrast: high`
- 良好的鍵盤導航支援
- 符合 WCAG 對比度標準

## 最佳實踐

1. **一致性** - 使用統一的主題變數和組件類
2. **性能** - 避免過度的動畫效果
3. **可訪問性** - 確保足夠的對比度
4. **響應式** - 考慮不同螢幕尺寸的體驗
5. **測試** - 在不同主題下測試所有組件
