<template>
  <v-layout>
    <v-navigation-drawer v-model="drawer" app>
      <v-list-item
        prepend-icon="mdi-bridge"
        title="PicaBridge"
        subtitle="管理后台"
      />
      <v-divider />
      <v-list density="compact" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.path"
          :prepend-icon="item.icon"
          :title="item.title"
          :to="item.path"
          rounded="xl"
        />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app density="comfortable">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-app-bar-title>PicaBridge 管理后台</v-app-bar-title>
      <v-spacer />
      <v-btn icon="mdi-logout" @click="handleLogout" />
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const drawer = ref(true)

const menuItems = [
  { title: '系统设置', icon: 'mdi-cog', path: '/ui/system' },
  { title: '分类管理', icon: 'mdi-tag-multiple', path: '/ui/categories' },
  { title: '公告管理', icon: 'mdi-bullhorn', path: '/ui/announcements' },
  { title: '关键词管理', icon: 'mdi-magnify', path: '/ui/keywords' },
  { title: '启动图管理', icon: 'mdi-image-multiple', path: '/ui/launch-image' },
  { title: '小程序管理', icon: 'mdi-apps', path: '/ui/apps' },
  { title: '备份与恢复', icon: 'mdi-backup-restore', path: '/ui/backup' },
]

function handleLogout() {
  auth.logout()
  router.push('/ui/login')
}
</script>
