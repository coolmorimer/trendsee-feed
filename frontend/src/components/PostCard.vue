<template>
  <div class="post-card" @click="$emit('select', post)">
    <div class="post-card-top">
      <div class="post-card-author" @click.stop>
        <router-link :to="`/profile/${post.user_id}`" class="author-link">
          <span class="author-avatar">{{ post.author_name?.charAt(0)?.toUpperCase() || post.user_id }}</span>
          <span class="author-label">{{ post.author_name || 'Автор #' + post.user_id }}</span>
        </router-link>
      </div>
      <time class="post-card-date">{{ formattedDate }}</time>
    </div>
    <h3 class="post-card-title">{{ post.title }}</h3>
    <p class="post-card-text">{{ truncatedText }}</p>
  </div>
</template>

<script setup>
// Карточка поста в ленте. Клик по автору — профиль, клик по карточке — модалка.

import { computed } from 'vue'

const props = defineProps({
  post: { type: Object, required: true },
})

defineEmits(['select'])

const truncatedText = computed(() => {
  const text = props.post.text
  return text.length > 150 ? text.slice(0, 150) + '…' : text
})

const formattedDate = computed(() => {
  return new Date(props.post.created_at).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
})
</script>

<style scoped>
.post-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius);
  padding: 1.25rem 1.5rem;
  cursor: pointer;
  transition: all var(--transition);
  position: relative;
}

.post-card::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: var(--radius);
  background: var(--gradient-primary);
  opacity: 0;
  z-index: -1;
  transition: opacity var(--transition);
}

.post-card:hover {
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow);
}

.post-card:hover::before {
  opacity: 0.15;
}

.post-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.post-card-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: inherit;
  border-radius: var(--radius-xs);
  padding: 0.15rem 0.4rem 0.15rem 0;
  transition: all var(--transition);
}

.author-link:hover {
  color: var(--color-primary);
}

.author-link:hover .author-label {
  color: var(--color-primary);
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  font-weight: 700;
  color: #fff;
}

.author-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.post-card-date {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.post-card-title {
  font-size: 1.05rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: var(--color-text);
  line-height: 1.4;
}

.post-card-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.55;
}
</style>
