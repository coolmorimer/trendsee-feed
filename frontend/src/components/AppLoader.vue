<template>
  <div class="loader">
    <div class="loader__spinner"></div>
    <p v-if="text" class="loader__text">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '' },
})
</script>

<style scoped>
.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2.5rem;
  gap: 1rem;
}

.loader__spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--color-border-subtle);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loader__text {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}
</style>
