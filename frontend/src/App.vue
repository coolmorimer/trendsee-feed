<template>
  <div id="app-root">
    <header class="app-header">
      <div class="container header-inner">
        <router-link to="/" class="logo">
          <span class="logo-icon">&#9670;</span>
          <span>Trendsee</span>
        </router-link>
        <nav class="nav">
          <router-link to="/auth" class="nav-link">Вход</router-link>
          <router-link to="/feed" class="nav-link">Лента</router-link>
          <button class="theme-toggle" @click="toggle" :title="theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'">
            <svg v-if="theme === 'dark'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </button>
        </nav>
      </div>
    </header>
    <main class="container main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useTheme } from './composables/useTheme'

const { theme, toggle } = useTheme()
</script>

<style scoped>
.app-header {
  background: rgba(8, 8, 15, 0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--color-border-subtle);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: background var(--transition-slow);
}

[data-theme="light"] .app-header {
  background: rgba(255, 255, 255, 0.85);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.35rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-decoration: none;
}

.logo-icon {
  font-size: 1.1rem;
}

.nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.nav-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  transition: all var(--transition);
}

.nav-link:hover {
  color: var(--color-text);
  background: rgba(139, 92, 246, 0.1);
}

.nav-link.router-link-active {
  color: var(--color-primary);
  background: rgba(139, 92, 246, 0.1);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  margin-left: 0.5rem;
  transition: all var(--transition);
}

.theme-toggle:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: rgba(139, 92, 246, 0.1);
}

.main-content {
  padding-top: 2rem;
  padding-bottom: 4rem;
}
</style>
