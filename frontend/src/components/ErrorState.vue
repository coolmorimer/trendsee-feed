<template>
  <div class="error-state">
    <div class="error-state__icon">⚠️</div>
    <h3 class="error-state__title">Что-то пошло не так</h3>
    <p class="error-state__text">{{ message }}</p>
    <button v-if="retryable" class="error-state__btn" @click="$emit('retry')">Попробовать снова</button>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: 'Не удалось загрузить данные. Попробуйте ещё раз.' },
  retryable: { type: Boolean, default: true },
})

defineEmits(['retry'])
</script>

<style scoped>
.error-state {
  text-align: center;
  padding: 5rem 2rem;
}

.error-state__icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.error-state__title {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-danger);
}

.error-state__text {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}

.error-state__btn {
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
  transition: all var(--transition);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.error-state__btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}
</style>
