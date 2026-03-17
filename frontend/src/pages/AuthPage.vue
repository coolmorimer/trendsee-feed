<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-card__title">Добро пожаловать в Trendsee</h1>
      <p class="auth-card__subtitle">Войдите по User ID или создайте новый аккаунт</p>

      <!-- Tab switcher -->
      <div class="auth-tabs">
        <button
          :class="['auth-tab', { active: mode === 'login' }]"
          @click="mode = 'login'"
        >
          Войти
        </button>
        <button
          :class="['auth-tab', { active: mode === 'register' }]"
          @click="mode = 'register'"
        >
          Регистрация
        </button>
      </div>

      <!-- Login -->
      <form v-if="mode === 'login'" class="auth-form" @submit.prevent="handleLogin">
        <label class="form-label">
          ID пользователя
          <input
            v-model.number="userId"
            type="number"
            class="form-input"
            placeholder="Введите ваш ID"
            min="1"
            required
          />
        </label>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Загрузка…' : 'Получить токен и войти' }}
        </button>
      </form>

      <!-- Register -->
      <form v-else class="auth-form" @submit.prevent="handleRegister">
        <label class="form-label">
          Имя
          <input
            v-model="name"
            type="text"
            class="form-input"
            placeholder="Введите ваше имя"
            minlength="1"
            required
          />
        </label>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Создание…' : 'Создать аккаунт' }}
        </button>
      </form>

      <!-- Messages -->
      <Transition name="fade">
        <div v-if="error" class="auth-message auth-message--error">{{ error }}</div>
      </Transition>
      <Transition name="fade">
        <div v-if="success" class="auth-message auth-message--success">{{ success }}</div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
// Страница входа/регистрации. Логин по user ID, регистрация по имени.

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { userApi } from '../services/api'

const router = useRouter()

const mode = ref('login')
const userId = ref(null)
const name = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

function clearMessages() {
  error.value = ''
  success.value = ''
}

async function handleLogin() {
  clearMessages()
  if (!userId.value || userId.value < 1) {
    error.value = 'Введите корректный ID пользователя'
    return
  }
  loading.value = true
  try {
    const { data } = await userApi.getToken(userId.value)
    localStorage.setItem('token', data.token)
    localStorage.setItem('userId', String(userId.value))
    // Получаем имя пользователя для отображения в шапке
    try {
      const { data: userData } = await userApi.getById(userId.value)
      localStorage.setItem('userName', userData.name)
    } catch {
      // некритично, имя просто не будет отображаться
    }
    success.value = 'Авторизация успешна! Перенаправление…'
    setTimeout(() => router.push('/feed'), 500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Пользователь не найден'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  clearMessages()
  if (!name.value.trim()) {
    error.value = 'Введите имя'
    return
  }
  loading.value = true
  try {
    const { data } = await userApi.create(name.value.trim())
    localStorage.setItem('token', data.token)
    localStorage.setItem('userId', String(data.user.id))
    localStorage.setItem('userName', data.user.name)
    success.value = `Аккаунт создан! Ваш ID: ${data.user.id}. Перенаправление…`
    setTimeout(() => router.push('/feed'), 800)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось создать аккаунт'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 4rem;
  min-height: calc(100vh - 64px - 6rem);
}

.auth-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 2.5rem;
  max-width: 440px;
  width: 100%;
  box-shadow: var(--shadow-glow);
}

.auth-card__title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.auth-card__subtitle {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: 1.75rem;
}

.auth-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 1.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--color-bg);
}

.auth-tab {
  flex: 1;
  padding: 0.65rem;
  font-size: 0.9rem;
  font-weight: 500;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  transition: all var(--transition);
}

.auth-tab.active {
  background: var(--gradient-primary);
  color: white;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.form-input {
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  outline: none;
  background: var(--color-bg-elevated);
  color: var(--color-text);
  transition: border-color var(--transition), box-shadow var(--transition);
}

.form-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
}

.form-input::placeholder {
  color: var(--color-text-muted);
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 0.8rem;
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  font-weight: 600;
  transition: all var(--transition);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.auth-message {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
}

.auth-message--error {
  background: rgba(244, 63, 94, 0.1);
  color: var(--color-danger);
  border: 1px solid rgba(244, 63, 94, 0.2);
}

.auth-message--success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}
</style>
