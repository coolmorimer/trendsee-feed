// Бесконечный скролл. Триггерится когда до конца страницы остаётся < threshold пикселей.
// ИИ подсказал комбинацию requestAnimationFrame + passive: true —
// без RAF scroll-обработчик дёргается слишком часто, а passive нужен чтобы браузер не тормозил скролл.

import { ref, onMounted, onUnmounted } from 'vue'

export function useInfiniteScroll(loadMore, { threshold = 500 } = {}) {
  const isLoading = ref(false)
  const hasMore = ref(true)
  const error = ref(null)

  async function check() {
    if (isLoading.value || !hasMore.value) return

    const scrollHeight = document.documentElement.scrollHeight
    const scrollTop = window.scrollY || document.documentElement.scrollTop
    const clientHeight = window.innerHeight

    if (scrollHeight - scrollTop - clientHeight < threshold) {
      isLoading.value = true
      error.value = null
      try {
        const more = await loadMore()
        hasMore.value = more
      } catch (e) {
        error.value = e
      } finally {
        isLoading.value = false
      }
    }
  }

  let handler = null

  onMounted(() => {
    let ticking = false
    handler = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          check()
          ticking = false
        })
        ticking = true
      }
    }
    window.addEventListener('scroll', handler, { passive: true })
  })

  onUnmounted(() => {
    if (handler) {
      window.removeEventListener('scroll', handler)
    }
  })

  function reset() {
    hasMore.value = true
    error.value = null
    isLoading.value = false
  }

  return { isLoading, hasMore, error, reset, check }
}
