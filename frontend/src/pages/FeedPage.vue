<template>
  <div class="feed-page">
    <div class="feed-header">
      <div class="feed-header-left">
        <h1 class="feed-title">Лента</h1>
        <span class="feed-subtitle">Все публикации</span>
      </div>
      <div class="feed-header-right" v-if="currentUserId">
        <div class="user-menu-wrapper">
          <button class="user-badge" @click="showProfileMenu = !showProfileMenu">
            <span class="user-avatar">{{ currentUserName?.charAt(0)?.toUpperCase() || currentUserId }}</span>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M3 4.5L6 7.5L9 4.5"/></svg>
          </button>

          <Transition name="slide">
            <div v-if="showProfileMenu" class="profile-dropdown" @click.stop>
              <div class="dropdown-header">{{ currentUserName || 'Пользователь #' + currentUserId }}</div>
              <form class="dropdown-form" @submit.prevent="handleUpdateName">
                <input
                  v-model="newUserName"
                  type="text"
                  class="dropdown-input"
                  placeholder="Новое имя"
                  minlength="1"
                  required
                />
                <button type="submit" class="dropdown-btn-save" :disabled="updatingName">
                  {{ updatingName ? '…' : 'Сохранить' }}
                </button>
              </form>
              <Transition name="fade">
                <div v-if="profileMessage" class="dropdown-msg" :class="profileMessageType">
                  {{ profileMessage }}
                </div>
              </Transition>
              <div class="dropdown-divider"></div>
              <button class="dropdown-btn-danger" @click="handleDeleteUser">Удалить аккаунт</button>
              <button class="dropdown-btn-logout" @click="logout">Выйти</button>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <Transition name="fade">
      <div v-if="currentUserId && showCreateForm" class="create-card">
        <div class="create-card-header">
          <h3 class="create-card-title">Новая публикация</h3>
          <button class="create-card-close" @click="showCreateForm = false">&times;</button>
        </div>
        <form @submit.prevent="handleCreatePost">
          <input
            v-model="newPostTitle"
            type="text"
            class="create-input"
            placeholder="Заголовок"
            maxlength="200"
            required
          />
          <textarea
            v-model="newPostText"
            class="create-textarea"
            placeholder="О чём хотите написать?"
            rows="4"
            required
          ></textarea>
          <div class="create-actions">
            <button type="button" class="btn-ghost" @click="showCreateForm = false">Отмена</button>
            <button type="submit" class="btn-accent" :disabled="creatingPost">
              {{ creatingPost ? 'Публикация…' : 'Опубликовать' }}
            </button>
          </div>
          <Transition name="fade">
            <div v-if="createError" class="create-error">{{ createError }}</div>
          </Transition>
        </form>
      </div>
    </Transition>

    <button
      v-if="currentUserId && !showCreateForm"
      class="btn-new-post"
      @click="showCreateForm = true"
    >
      <span class="btn-new-post-icon">+</span>
      Новая публикация
    </button>

    <AppLoader v-if="initialLoading" text="Загрузка публикаций…" />

    <ErrorState
      v-else-if="fetchError && posts.length === 0"
      :message="fetchError"
      @retry="loadInitial"
    />

    <EmptyState v-else-if="!initialLoading && posts.length === 0" />

    <div v-else class="feed-list">
      <PostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
        @select="selectedPost = post"
      />

      <AppLoader v-if="isLoading" text="Загрузка ещё…" />

      <div v-if="!hasMore && posts.length > 0" class="feed-end">
        Вы просмотрели все публикации
      </div>
    </div>

    <PostModal
      :post="selectedPost"
      :currentUserId="Number(currentUserId)"
      @close="selectedPost = null"
      @updated="onPostUpdated"
      @deleted="onPostDeleted"
    />
  </div>
</template>

<script setup>
// Лента: показываем посты всех юзеров с бесконечным скроллом.
// Неавторизованные могут читать, но не могут писать.

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userApi, postApi } from '../services/api'
import { useInfiniteScroll } from '../composables/useInfiniteScroll'
import PostCard from '../components/PostCard.vue'
import PostModal from '../components/PostModal.vue'
import AppLoader from '../components/AppLoader.vue'
import EmptyState from '../components/EmptyState.vue'
import ErrorState from '../components/ErrorState.vue'

const router = useRouter()

const posts = ref([])
const selectedPost = ref(null)
const initialLoading = ref(true)
const fetchError = ref('')
const currentUserId = ref(localStorage.getItem('userId'))
const currentUserName = ref(localStorage.getItem('userName') || '')
const LIMIT = 20
let offset = 0
// дедупликация по ID — иначе при infinite scroll могут повторяться карточки
const existingIds = new Set()

const showCreateForm = ref(false)
const newPostTitle = ref('')
const newPostText = ref('')
const creatingPost = ref(false)
const createError = ref('')

const showProfileMenu = ref(false)
const newUserName = ref('')
const updatingName = ref(false)
const profileMessage = ref('')
const profileMessageType = ref('')

async function handleCreatePost() {
  createError.value = ''
  creatingPost.value = true
  try {
    await postApi.create(newPostTitle.value.trim(), newPostText.value.trim())
    newPostTitle.value = ''
    newPostText.value = ''
    showCreateForm.value = false
    await loadInitial()
  } catch (e) {
    createError.value = e.response?.data?.detail || 'Не удалось создать публикацию'
  } finally {
    creatingPost.value = false
  }
}

async function handleUpdateName() {
  if (!newUserName.value.trim()) return
  updatingName.value = true
  profileMessage.value = ''
  try {
    await userApi.update(currentUserId.value, newUserName.value.trim())
    profileMessage.value = 'Имя обновлено'
    profileMessageType.value = 'success'
    currentUserName.value = newUserName.value.trim()
    localStorage.setItem('userName', currentUserName.value)
    newUserName.value = ''
  } catch (e) {
    profileMessage.value = e.response?.data?.detail || 'Не удалось обновить имя'
    profileMessageType.value = 'error'
  } finally {
    updatingName.value = false
  }
}

async function handleDeleteUser() {
  if (!confirm('Вы уверены, что хотите удалить аккаунт? Все публикации будут удалены.')) return
  try {
    await userApi.delete(currentUserId.value)
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('userName')
    router.push('/auth')
  } catch (e) {
    profileMessage.value = e.response?.data?.detail || 'Не удалось удалить аккаунт'
    profileMessageType.value = 'error'
  }
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
}

async function loadMore() {
  const { data } = await postApi.getAll({ limit: LIMIT, offset })
  const newItems = data.items.filter((item) => !existingIds.has(item.id))
  newItems.forEach((item) => existingIds.add(item.id))
  posts.value.push(...newItems)
  offset += LIMIT
  return data.has_more
}

const { isLoading, hasMore, error, reset } = useInfiniteScroll(loadMore)

async function loadInitial() {
  initialLoading.value = true
  fetchError.value = ''
  offset = 0
  posts.value = []
  existingIds.clear()
  reset()
  try {
    const more = await loadMore()
    hasMore.value = more
  } catch (e) {
    fetchError.value = e.response?.data?.detail || 'Не удалось загрузить публикации'
  } finally {
    initialLoading.value = false
  }
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userId')
  localStorage.removeItem('userName')
  router.push('/auth')
}

onMounted(() => {
  loadInitial()
})
</script>

<style scoped>
.feed-page {
  max-width: 800px;
  margin: 0 auto;
}

/* Header */
.feed-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.75rem;
}

.feed-header-left {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.feed-title {
  font-size: 1.75rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.feed-subtitle {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

/* User badge / menu */
.user-menu-wrapper {
  position: relative;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 0.4rem 0.75rem 0.4rem 0.4rem;
  border-radius: 100px;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  transition: all var(--transition);
}

.user-badge:hover {
  border-color: var(--color-primary);
  color: var(--color-text);
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  color: #fff;
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 0.75rem;
  min-width: 260px;
  box-shadow: var(--shadow-lg);
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dropdown-header {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  padding: 0.25rem 0.25rem 0.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
  margin-bottom: 0.25rem;
}

.dropdown-form {
  display: flex;
  gap: 0.4rem;
}

.dropdown-input {
  flex: 1;
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xs);
  font-size: 0.8rem;
  background: var(--color-bg);
  color: var(--color-text);
  outline: none;
  transition: border-color var(--transition);
}

.dropdown-input:focus {
  border-color: var(--color-primary);
}

.dropdown-input::placeholder {
  color: var(--color-text-muted);
}

.dropdown-btn-save {
  padding: 0.4rem 0.65rem;
  border-radius: var(--radius-xs);
  font-size: 0.75rem;
  font-weight: 600;
  border: none;
  background: var(--gradient-primary);
  color: #fff;
  transition: opacity var(--transition);
  white-space: nowrap;
}

.dropdown-btn-save:hover:not(:disabled) {
  opacity: 0.85;
}

.dropdown-msg {
  font-size: 0.75rem;
  padding: 0.3rem 0.5rem;
  border-radius: var(--radius-xs);
}

.dropdown-msg.success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.dropdown-msg.error {
  background: rgba(244, 63, 94, 0.1);
  color: var(--color-danger);
}

.dropdown-divider {
  height: 1px;
  background: var(--color-border-subtle);
  margin: 0.25rem 0;
}

.dropdown-btn-danger,
.dropdown-btn-logout {
  width: 100%;
  padding: 0.45rem 0.6rem;
  border-radius: var(--radius-xs);
  font-size: 0.8rem;
  font-weight: 500;
  border: none;
  background: transparent;
  text-align: left;
  transition: all var(--transition);
}

.dropdown-btn-danger {
  color: var(--color-danger);
}

.dropdown-btn-danger:hover {
  background: rgba(244, 63, 94, 0.1);
}

.dropdown-btn-logout {
  color: var(--color-text-secondary);
}

.dropdown-btn-logout:hover {
  color: var(--color-text);
  background: var(--color-hover-overlay);
}

/* New post button */
.btn-new-post {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 1rem 1.25rem;
  background: var(--color-surface);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius);
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
  transition: all var(--transition);
}

.btn-new-post:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: rgba(139, 92, 246, 0.05);
}

.btn-new-post-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  color: #fff;
  font-weight: 300;
}

/* Create card */
.create-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-glow);
}

.create-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.create-card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.create-card-close {
  background: none;
  border: none;
  font-size: 1.3rem;
  color: var(--color-text-muted);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}

.create-card-close:hover {
  background: var(--color-hover-overlay);
  color: var(--color-text);
}

.create-input,
.create-textarea {
  width: 100%;
  padding: 0.7rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  background: var(--color-bg);
  color: var(--color-text);
  outline: none;
  margin-bottom: 0.75rem;
  transition: border-color var(--transition), box-shadow var(--transition);
}

.create-input:focus,
.create-textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
}

.create-input::placeholder,
.create-textarea::placeholder {
  color: var(--color-text-muted);
}

.create-textarea {
  resize: vertical;
  min-height: 80px;
}

.create-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-ghost {
  padding: 0.55rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  transition: all var(--transition);
}

.btn-ghost:hover {
  border-color: var(--color-text-muted);
  color: var(--color-text);
}

.btn-accent {
  padding: 0.55rem 1.25rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
  border: none;
  background: var(--gradient-primary);
  color: #fff;
  transition: all var(--transition);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.btn-accent:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

.btn-accent:disabled {
  opacity: 0.5;
}

.create-error {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--color-danger);
  background: rgba(244, 63, 94, 0.1);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-xs);
}

/* Feed list */
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
