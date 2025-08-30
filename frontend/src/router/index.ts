import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    redirect: '/search'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresGuest: true } // 只有未登录用户才能访问
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/SearchView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/ProjectsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:id/documents',
    name: 'ProjectDocuments',
    component: () => import('@/views/ProjectDocumentsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/documents',
    name: 'Documents', 
    component: () => import('@/views/DocumentsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/chat/ChatView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/compare',
    name: 'Compare',
    component: () => import('@/views/CompareView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  // 使用 history 模式，适合 Web 应用
  history: createWebHashHistory('/scdlsearch/'),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  // 初始化认证状态（只在首次访问时）
  if (!authStore.user && !authStore.token) {
    authStore.initAuth()
  }
  
  const requiresAuth = to.meta.requiresAuth
  const requiresGuest = to.meta.requiresGuest
  const isAuthenticated = authStore.isAuthenticated
  
  if (requiresAuth && !isAuthenticated) {
    // 需要认证但未登录，跳转到登录页
    next('/login')
  } else if (requiresGuest && isAuthenticated) {
    // 已登录用户访问登录页，跳转到首页
    next('/search')
  } else {
    next()
  }
})

export default router