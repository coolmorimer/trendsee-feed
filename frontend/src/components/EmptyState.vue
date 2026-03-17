<template>
  <div class="empty-state">
    <div class="empty-state__icon">📭</div>
    <h3 class="empty-state__title">{{ title }}</h3>
    <p class="empty-state__text">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Публикаций пока нет' },
  message: { type: String, default: 'Здесь пока ничего нет. Загляните позже!' },
})
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 5rem 2rem;
}

.empty-state__icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.empty-state__title {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-text);
}

.empty-state__text {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}
</style>
