// HTTP-клиент для работы с API. Токен автоматом подставляется из localStorage.

import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

// интерцептор: если есть токен — кидаем Bearer
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const userApi = {
  create(name) {
    return api.post('/users', { name })
  },
  getById(userId) {
    return api.get(`/users/${userId}`)
  },
  getToken(userId) {
    return api.get(`/users/${userId}/token`)
  },
  update(userId, name) {
    return api.patch(`/users/${userId}`, { name })
  },
  delete(userId) {
    return api.delete(`/users/${userId}`)
  },
  getPosts(userId, { limit = 20, offset = 0 } = {}) {
    return api.get(`/users/${userId}/posts`, { params: { limit, offset } })
  },
}

export const postApi = {
  getAll({ limit = 20, offset = 0 } = {}) {
    return api.get('/posts', { params: { limit, offset } })
  },
  create(title, text) {
    return api.post('/posts', { title, text })
  },
  update(postId, data) {
    return api.patch(`/posts/${postId}`, data)
  },
  delete(postId) {
    return api.delete(`/posts/${postId}`)
  },
}

export default api
