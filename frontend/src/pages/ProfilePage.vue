<template>
  <div class="profile-page">
    <div class="profile-header">
      <router-link to="/feed" class="back-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Назад к ленте
      </router-link>
    </div>

    <div class="profile-card">
      <div class="profile-avatar">{{ authorInitial }}</div>
      <div class="profile-info">
        <h1 class="profile-name">{{ authorName }}</h1>
        <span class="profile-posts-count" v-if="total !== null">{{ total }} {{ pluralPosts(total) }}</span>
      </div>
    </div>

    <AppLoader v-if="initialLoading" text="Загрузка публикаций…" />

    <ErrorState
      v-else-if="fetchError && posts.length === 0"
      :message="fetchError"
      @retry="loadInitial"
    />

    <EmptyState
      v-else-if="!initialLoading && posts.length === 0"
      title="Нет публикаций"
      message="У этого автора пока нет публикаций."
    />

    <div v-else class="feed-list">
      <PostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
        @select="selectedPost = post"
      />

      <AppLoader v-if="isLoading" text="Загрузка ещё…" />

      <div v-if="!hasMore && posts.length > 0" class="feed-end">
        Все публикации автора
      </div>
    </div>

    <PostModal
      :post="selectedPost"
      :currentUserId="Number(currentAuthUserId)"
      @close="selectedPost = null"
      @updated="onPostUpdated"
      @deleted="onPostDeleted"
    />
  </div>
</template>

<script setup>
// Страница профиля автора — показываем все его посты

import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { userApi } from '../services/api'
import { useInfiniteScroll } from '../composables/useInfiniteScroll'
import PostCard from '../components/PostCard.vue'
import PostModal from '../components/PostModal.vue'
import AppLoader from '../components/AppLoader.vue'
import EmptyState from '../components/EmptyState.vue'
import ErrorState from '../components/ErrorState.vue'

const props = defineProps({
  userId: { type: String, required: true },
})

const posts = ref([])
const selectedPost = ref(null)
const initialLoading = ref(true)
const fetchError = ref('')
const total = ref(null)
const authorData = ref(null)  // данные профиля — загружаем отдельно чтобы имя было даже без постов
const currentAuthUserId = ref(localStorage.getItem('userId'))
const LIMIT = 20
let offset = 0
const existingIds = new Set()

const authorName = computed(() => {
  if (authorData.value) return authorData.value.name
  if (posts.value.length > 0 && posts.value[0].author_name) {
    return posts.value[0].author_name
  }
  return 'Автор #' + props.userId
})

const authorInitial = computed(() => {
  const name = authorName.value
  if (name && !name.startsWith('Автор #')) {
    return name.charAt(0).toUpperCase()
  }
  return props.userId
})

// ИИ помог с русской плюрализацией — правила склонения
// для слова "публикация" с учётом 11-19 и т.д.
function pluralPosts(n) {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return 'публикация'
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return 'публикации'
  return 'публикаций'
}

function onPostUpdated(updatedPost) {
  const idx = posts.value.findIndex((p) => p.id === updatedPost.id)
  if (idx !== -1) posts.value[idx] = updatedPost
  selectedPost.value = null
}

function onPostDeleted(postId) {
  posts.value = posts.value.filter((p) => p.id !== postId)
  existingIds.delete(postId)
  selectedPost.value = null
  if (total.value !== null) total.value--
}

async function loadMore() {
  const { data } = await userApi.getPosts(props.userId, { limit: LIMIT, offset })
  total.value = data.total
  const newItems = data.items.filter((item) => !existingIds.has(item.id))
  newItems.forEach((item) => existingIds.add(item.id))
  posts.value.push(...newItems)
  offset += LIMIT
  return data.has_more
}

const { isLoading, hasMore, error, reset, check } = useInfiniteScroll(loadMore)

async function loadInitial() {
  initialLoading.value = true
  fetchError.value = ''
  offset = 0
  posts.value = []
  existingIds.clear()
  authorData.value = null
  reset()
  try {
    // загружаем данные пользователя и первую страницу постов параллельно
    const [more] = await Promise.all([
      loadMore(),
      userApi.getById(props.userId)
        .then(({ data }) => { authorData.value = data })
        .catch(() => {}),
    ])
    hasMore.value = more
    if (more) {
      await nextTick()
      check()
    }
  } catch (e) {
    fetchError.value = e.response?.data?.detail || 'Не удалось загрузить публикации'
  } finally {
    initialLoading.value = false
  }
}

watch(() => props.userId, () => {
  loadInitial()
})

onMounted(() => {
  loadInitial()
})
</script>

<style scoped>
.profile-page {
  max-width: 800px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: 1.5rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  padding: 0.4rem 0.6rem;
  border-radius: var(--radius-xs);
  transition: all var(--transition);
}

.back-link:hover {
  color: var(--color-primary);
  background: rgba(139, 92, 246, 0.1);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-glow);
}

.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.profile-name {
  font-size: 1.35rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.profile-posts-count {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.feed-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.feed-end {
  text-align: center;
  padding: 2.5rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}
</style>
