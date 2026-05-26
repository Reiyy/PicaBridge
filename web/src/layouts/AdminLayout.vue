<template>
  <v-layout>
    <v-navigation-drawer v-model="drawer" app color="surface-container-low">
      <v-list-item
        title="PicaBridge"
        subtitle="管理后台"
      >
        <template #prepend>
          <img :src="`${baseUrl}img/picabridge.png`" alt="PicaBridge" style="width: 32px; height: 32px; border-radius: 7px; margin-right: 12px;">
        </template>
      </v-list-item>
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

    <v-app-bar app density="comfortable" color="surface-container">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-app-bar-title>PicaBridge 管理后台</v-app-bar-title>
      <v-spacer />
      <v-btn
        v-if="restartStore.restartRequired"
        color="error"
        size="small"
        variant="outlined"
        :loading="restartStore.restarting"
        :disabled="restartStore.restarting"
        prepend-icon="mdi-restart"
        @click="onRestart"
        class="mr-2 restart-btn"
      >
        立即重启
      </v-btn>
      <v-btn icon="mdi-logout" @click="handleLogout" />
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useRestartStore } from '../stores/restart'
import request from '../api/request'

const baseUrl = import.meta.env.BASE_URL
const router = useRouter()
const auth = useAuthStore()
const restartStore = useRestartStore()
const drawer = ref(true)
const snackbar = ref({ show: false, text: '', color: 'success' })

const menuItems = [
  { title: '主页', icon: 'mdi-home', path: '/ui/dashboard' },
  { title: '系统设置', icon: 'mdi-cog', path: '/ui/system' },
  { title: '分类管理', icon: 'mdi-tag-multiple', path: '/ui/categories' },
  { title: '公告管理', icon: 'mdi-bullhorn', path: '/ui/announcements' },
  { title: '关键词管理', icon: 'mdi-magnify', path: '/ui/keywords' },
  { title: '启动图管理', icon: 'mdi-image-multiple', path: '/ui/launch-image' },
  { title: '小程序管理', icon: 'mdi-apps', path: '/ui/apps' },
  { title: '用户管理', icon: 'mdi-account-group', path: '/ui/users' },
  { title: '备份与恢复', icon: 'mdi-backup-restore', path: '/ui/backup' },
  { title: '主题设置', icon: 'mdi-palette', path: '/ui/theme' },
]

async function onRestart() {
  const result = await restartStore.handleRestart()
  if (result.status === 'completed') {
    snackbar.value = { show: true, text: '服务已重启完成', color: 'success' }
  } else if (result.status === 'timeout') {
    snackbar.value = { show: true, text: '重启超时，请手动检查服务状态', color: 'warning' }
  } else {
    snackbar.value = { show: true, text: result.message || '重启失败', color: 'error' }
  }
}

function handleLogout() {
  auth.logout()
  router.push('/ui/login')
}
</script>

<style scoped>
.restart-btn {
  border: 2px solid rgb(var(--v-theme-error)) !important;
  animation: restart-pulse 1.5s ease-in-out infinite;
}

@keyframes restart-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
