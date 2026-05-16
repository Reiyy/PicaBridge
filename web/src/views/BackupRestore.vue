<template>
  <div>
    <h2 class="text-h5 mb-4">备份与恢复</h2>

    <v-card class="mb-4">
      <v-card-title>创建备份</v-card-title>
      <v-card-text>
        <p class="text-medium-emphasis mb-4">下载当前配置文件到浏览器</p>
        <v-btn color="primary" :loading="backupLoading" @click="createBackup" prepend-icon="mdi-backup-restore">
          创建备份
        </v-btn>
      </v-card-text>
    </v-card>

    <v-card>
      <v-card-title>恢复备份</v-card-title>
      <v-card-text>
        <p class="text-medium-emphasis mb-4">选择之前下载的备份文件来恢复配置</p>
        <v-file-input v-model="restoreFile" label="选择备份文件" accept=".json" density="compact" prepend-icon="mdi-file-upload" class="mb-2" />
        <v-btn color="warning" :loading="restoreLoading" :disabled="!restoreFile" @click="restoreBackup" prepend-icon="mdi-restore">
          恢复备份
        </v-btn>
        <v-btn
          v-if="hasChanges"
          color="error"
          :loading="restarting"
          :disabled="restoreLoading"
          @click="handleRestart"
          class="ml-2"
          prepend-icon="mdi-restart"
        >
          立即重启
        </v-btn>
      </v-card-text>
    </v-card>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">{{ snackbar.text }}</v-snackbar>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import request from '../api/request'

const backupLoading = ref(false)
const restoreLoading = ref(false)
const restarting = ref(false)
const hasChanges = ref(false)
const restoreFile = ref(null)
const snackbar = ref({ show: false, text: '', color: 'success' })

async function createBackup() {
  backupLoading.value = true
  try {
    const res = await fetch('/pbapi/config/backup', {
      method: 'POST',
      headers: { Authorization: localStorage.getItem('token') || '' },
    })
    if (!res.ok) throw new Error('备份失败')
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = res.headers.get('Content-Disposition')?.match(/filename="?(.+)"?/)?.[1] || 'PicaBridge_bak.json'
    a.click()
    URL.revokeObjectURL(url)
    snackbar.value = { show: true, text: '备份已下载', color: 'success' }
  } catch (e) {
    snackbar.value = { show: true, text: e.message || '备份失败', color: 'error' }
  } finally {
    backupLoading.value = false
  }
}

async function handleRestart() {
  restarting.value = true
  try {
    await request.post('/pbapi/restart')
    snackbar.value = { show: true, text: '服务正在重启...', color: 'info' }
    for (let i = 0; i < 10; i++) {
      await new Promise(r => setTimeout(r, 1000))
      try {
        await request.get('/pbapi/config')
        snackbar.value = { show: true, text: '服务已重启完成', color: 'success' }
        hasChanges.value = false
        return
      } catch { /* 服务还在重启中 */ }
    }
    snackbar.value = { show: true, text: '重启超时，请手动检查服务状态', color: 'warning' }
  } catch (e) {
    snackbar.value = { show: true, text: e.message || '重启失败', color: 'error' }
  } finally {
    restarting.value = false
  }
}

async function restoreBackup() {
  const file = Array.isArray(restoreFile.value) ? restoreFile.value[0] : restoreFile.value
  if (!file) return
  restoreLoading.value = true
  try {
    const text = await file.text()
    const config = JSON.parse(text)
    await request.post('/pbapi/config/restore', { config })
    snackbar.value = { show: true, text: '配置已恢复', color: 'success' }
    hasChanges.value = true
  } catch (e) {
    snackbar.value = { show: true, text: e.message || '恢复失败', color: 'error' }
  } finally {
    restoreLoading.value = false
    restoreFile.value = null
  }
}
</script>
