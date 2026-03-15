<template>
  <Transition name="modal">
    <div v-if="post" class="modal-overlay" @click.self="handleClose">
      <div class="modal-content">
        <button class="modal-close" @click="handleClose" aria-label="Закрыть">&times;</button>

        <template v-if="!editing">
          <div class="modal-author">
            <span class="modal-avatar">{{ post.author_name?.charAt(0)?.toUpperCase() || post.user_id }}</span>
            <div>
              <router-link :to="`/profile/${post.user_id}`" class="modal-author-name" @click="handleClose">{{ post.author_name || 'Автор #' + post.user_id }}</router-link>
              <div class="modal-date">{{ formatDate(post.created_at) }}</div>
            </div>
          </div>
          <h2 class="modal-title">{{ post.title }}</h2>
          <p class="modal-text">{{ post.text }}</p>
          <div class="modal-footer">
            <span class="modal-updated">Обновлено: {{ formatDate(post.updated_at) }}</span>
            <div v-if="isOwner" class="modal-actions">
              <button class="btn-edit" @click="startEditing">Редактировать</button>
              <button class="btn-delete" @click="handleDelete" :disabled="deleting">
                {{ deleting ? 'Удаление…' : 'Удалить' }}
              </button>
            </div>
          </div>
        </template>

        <template v-else>
          <form class="edit-form" @submit.prevent="handleSave">
            <label class="edit-label">Заголовок</label>
            <input v-model="editTitle" type="text" class="edit-input" maxlength="200" required />
            <label class="edit-label">Текст</label>
            <textarea v-model="editText" class="edit-textarea" rows="6" required></textarea>
            <div class="edit-actions">
              <button type="button" class="btn-ghost" @click="cancelEditing">Отмена</button>
              <button type="submit" class="btn-save" :disabled="saving">
                {{ saving ? 'Сохранение…' : 'Сохранить' }}
              </button>
            </div>
            <Transition name="fade">
              <div v-if="editError" class="edit-error">{{ editError }}</div>
            </Transition>
          </form>
        </template>
      </div>
    </div>
  </Transition>
</template>

<script setup>
// Модальное окно поста: просмотр, редактирование и удаление (только владелец).

import { ref, computed, watch } from 'vue'
import { postApi } from '../services/api'

const props = defineProps({
  post: { type: Object, default: null },
  currentUserId: { type: Number, default: null },
})

const emit = defineEmits(['close', 'updated', 'deleted'])

const editing = ref(false)
const editTitle = ref('')
const editText = ref('')
const saving = ref(false)
const deleting = ref(false)
const editError = ref('')

const isOwner = computed(() => {
  return props.post && props.currentUserId && props.post.user_id === props.currentUserId
})

watch(() => props.post, () => {
  editing.value = false
  editError.value = ''
})

function startEditing() {
  editTitle.value = props.post.title
  editText.value = props.post.text
  editError.value = ''
  editing.value = true
}

function cancelEditing() {
  editing.value = false
  editError.value = ''
}

function handleClose() {
  editing.value = false
  editError.value = ''
  emit('close')
}

async function handleSave() {
  editError.value = ''
  saving.value = true
  try {
    const { data } = await postApi.update(props.post.id, {
      title: editTitle.value.trim(),
      text: editText.value.trim(),
    })
    editing.value = false
    emit('updated', data)
  } catch (e) {
    editError.value = e.response?.data?.detail || 'Не удалось сохранить изменения'
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!confirm('Удалить эту публикацию?')) return
  deleting.value = true
  try {
    await postApi.delete(props.post.id)
    emit('deleted', props.post.id)
  } catch (e) {
    editError.value = e.response?.data?.detail || 'Не удалось удалить публикацию'
  } finally {
    deleting.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--color-modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  backdrop-filter: blur(8px);
}

.modal-content {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 2rem;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-text-muted);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}

.modal-close:hover {
  background: var(--color-hover-overlay);
  color: var(--color-text);
}

.modal-author {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.25rem;
}

.modal-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  color: #fff;
}

.modal-author-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text);
  text-decoration: none;
  transition: color var(--transition);
}

.modal-author-name:hover {
  color: var(--color-primary);
}

.modal-date {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.modal-title {
  font-size: 1.35rem;
  font-weight: 700;
  margin-bottom: 1rem;
  padding-right: 2rem;
  line-height: 1.3;
}

.modal-text {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--color-text-secondary);
  white-space: pre-wrap;
}

.modal-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.modal-updated {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.modal-actions {
  display: flex;
  gap: 0.4rem;
}

.btn-edit {
  background: var(--gradient-primary);
  color: #fff;
  border: none;
  padding: 0.4rem 0.9rem;
  border-radius: var(--radius-xs);
  font-size: 0.8rem;
  font-weight: 600;
  transition: all var(--transition);
}

.btn-edit:hover {
  opacity: 0.85;
}

.btn-delete {
  background: transparent;
  border: 1px solid rgba(244, 63, 94, 0.3);
  color: var(--color-danger);
  padding: 0.4rem 0.9rem;
  border-radius: var(--radius-xs);
  font-size: 0.8rem;
  font-weight: 500;
  transition: all var(--transition);
}

.btn-delete:hover:not(:disabled) {
  background: var(--color-danger);
  border-color: var(--color-danger);
  color: #fff;
}

.btn-delete:disabled {
  opacity: 0.5;
}

/* Edit form */
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.edit-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.edit-input,
.edit-textarea {
  padding: 0.65rem 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  background: var(--color-bg);
  color: var(--color-text);
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
}

.edit-input:focus,
.edit-textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
}

.edit-textarea {
  resize: vertical;
  min-height: 100px;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-ghost {
  padding: 0.5rem 1rem;
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

.btn-save {
  background: var(--gradient-primary);
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
  transition: all var(--transition);
}

.btn-save:hover:not(:disabled) {
  opacity: 0.85;
}

.btn-save:disabled {
  opacity: 0.5;
}

.edit-error {
  font-size: 0.8rem;
  color: var(--color-danger);
  background: rgba(244, 63, 94, 0.1);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-xs);
}
</style>
