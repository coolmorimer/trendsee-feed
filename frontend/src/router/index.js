// Роуты: / -> лента (редирект), /auth, /feed, /profile/:userId

import { createRouter, createWebHistory } from 'vue-router'
import AuthPage from '../pages/AuthPage.vue'
import FeedPage from '../pages/FeedPage.vue'

import ProfilePage from '../pages/ProfilePage.vue'

const routes = [
  { path: '/', redirect: '/feed' },
  { path: '/auth', name: 'Auth', component: AuthPage },
  { path: '/feed', name: 'Feed', component: FeedPage },
  { path: '/profile/:userId', name: 'Profile', component: ProfilePage, props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
