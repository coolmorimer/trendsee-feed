// Переключение темы dark/light.
// ИИ подсказал про meta[theme-color] — без этого на мобилках
// панель браузера остаётся тёмной даже в светлой теме

import { ref, watchEffect } from 'vue'

const STORAGE_KEY = 'trendsee-theme'

// по умолчанию тёмная тема, но запоминаем выбор в localStorage
const theme = ref(localStorage.getItem(STORAGE_KEY) || 'dark')

function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t)
  const metaTheme = document.querySelector('meta[name="theme-color"]')
  if (metaTheme) {
    metaTheme.content = t === 'dark' ? '#08080f' : '#f8f9fc'
  }
}

applyTheme(theme.value)

watchEffect(() => {
  localStorage.setItem(STORAGE_KEY, theme.value)
  applyTheme(theme.value)
})

export function useTheme() {
  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  return { theme, toggle }
}
