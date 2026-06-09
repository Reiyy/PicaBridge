<template>
  <AppLayout
    app-name="PicaBridge"
    :user-name="auth.user?.name || '管理员'"
    :user-email="auth.user?.email || ''"
    :user-avatar="auth.user?.avatar || ''"
    :user-title="auth.user?.title || ''"
    :menu-items="menuItems"
  >
    <router-view />
  </AppLayout>
</template>

<script setup>
import AppLayout from '@/layouts/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const menuItems = [
  { title: '主页', icon: 'mdi-home', to: '/ui/dashboard' },
  { title: '系统设置', icon: 'mdi-cog', to: '/ui/system' },
  { title: '分类管理', icon: 'mdi-tag-multiple', to: '/ui/categories' },
  { title: '公告管理', icon: 'mdi-bullhorn', to: '/ui/announcements' },
  { title: '关键词管理', icon: 'mdi-magnify', to: '/ui/keywords' },
  { title: '启动图管理', icon: 'mdi-image-multiple', to: '/ui/launch-image' },
  { title: '小程序管理', icon: 'mdi-apps', to: '/ui/apps' },
  { title: '用户管理', icon: 'mdi-account-group', to: '/ui/users' },
  { title: '备份与恢复', icon: 'mdi-backup-restore', to: '/ui/backup' },
]
</script>
