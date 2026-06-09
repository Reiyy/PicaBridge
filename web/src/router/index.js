import { createRouter, createWebHistory } from 'vue-router'
import request from '../api/request'
import { useAuthStore } from '../stores/auth'

let initStatus = null

async function checkInit() {
  if (initStatus !== null) return initStatus
  try {
    const res = await request.get('/pbapi/init')
    initStatus = res.data === true
  } catch {
    initStatus = false
  }
  return initStatus
}

export function resetInitStatus() {
  initStatus = null
}

const routes = [
  {
    path: '/ui/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/ui/setup',
    name: 'Setup',
    component: () => import('../views/SetupView.vue'),
  },
  {
    path: '/ui/',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        redirect: '/ui/dashboard',
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
      },
      {
        path: 'system',
        name: 'System',
        component: () => import('../views/SystemSettings.vue'),
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/CategoryManage.vue'),
      },
      {
        path: 'announcements',
        name: 'Announcements',
        component: () => import('../views/AnnouncementManage.vue'),
      },
      {
        path: 'keywords',
        name: 'Keywords',
        component: () => import('../views/KeywordManage.vue'),
      },
      {
        path: 'launch-image',
        name: 'LaunchImage',
        component: () => import('../views/LaunchImageManage.vue'),
      },
      {
        path: 'apps',
        name: 'Apps',
        component: () => import('../views/AppsManage.vue'),
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/UserManage.vue'),
      },
      {
        path: 'backup',
        name: 'Backup',
        component: () => import('../views/BackupRestore.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const initialized = await checkInit()

  if (!initialized) {
    if (to.name === 'Setup') return next()
    return next('/ui/setup')
  }

  if (to.name === 'Setup') return next('/ui/login')

  if (to.name === 'Login') return next()

  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    return next('/ui/login')
  }

  // 页面刷新时，若 token 存在但用户信息未加载，自动获取
  if (token) {
    const auth = useAuthStore()
    if (!auth.user) {
      await auth.fetchUser()
    }
  }

  next()
})

export default router
