<template>
  <div>
    <h2 class="text-h5 mb-4">系统设置</h2>
    <v-skeleton-loader v-if="loading" type="card" />
    <template v-else>
      <v-form @submit.prevent="handleSave">
        <v-card class="mb-4">
          <v-card-title>服务器配置</v-card-title>
          <v-card-text>
            <v-text-field v-model="form.Listen" label="监听地址" />
            <v-text-field v-model="form.PicaBridge_URL" label="访问地址" />
            <v-text-field v-model="form.JWT_KEY" label="JWT 签名密钥" :placeholder="secrets.JWT_KEY ? '保持不变则留空' : ''" />
          </v-card-text>
        </v-card>

        <v-card class="mb-4">
          <v-card-title>LANraragi 配置</v-card-title>
          <v-card-text>
            <v-text-field v-model="form.lrr_Api" label="LANraragi API 地址" />
            <v-text-field v-model="form.lrr_Api_Key" label="API Key" :placeholder="secrets.lrr_Api_Key ? '保持不变则留空' : ''" />
          </v-card-text>
        </v-card>

        <v-card class="mb-4">
          <v-card-title>数据库配置</v-card-title>
          <v-card-text>
            <v-text-field v-model="form.db.host" label="主机" />
            <v-text-field v-model="form.db.user" label="用户" />
            <v-text-field v-model="form.db.password" label="密码" type="password" :placeholder="secrets['db.password'] ? '保持不变则留空' : ''" />
            <v-text-field v-model="form.db.name" label="数据库名" />
            <v-expansion-panels>
              <v-expansion-panel title="连接池配置">
                <v-expansion-panel-text>
                  <v-text-field v-model.number="form.db.pool.maxconnections" label="最大连接数" type="number" />
                  <v-text-field v-model.number="form.db.pool.mincached" label="最小连接数" type="number" />
                  <v-switch color="primary" v-model="form.db.pool.blocking" label="连接数耗尽时等待" />
                  <v-text-field v-model.number="form.db.pool.ping" label="健康检查策略" type="number" />
                  <v-switch color="primary" v-model="form.db.pool.reset" label="连接归还时重置" />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card-text>
        </v-card>

        <v-card class="mb-4">
          <v-card-title>资源映射</v-card-title>
          <v-card-text>
            <v-text-field v-model="form.lrr_Api" label="lrr_img" density="compact" readonly hint="LRR资源访问(自动管理，不可修改)" persistent-hint class="mb-2" />
            <v-text-field v-model="form.PicaBridge_URL" label="assets" density="compact" readonly hint="哔咔桥资源访问(自动管理，不可修改)" persistent-hint class="mb-2" />
            <v-divider class="my-3" />
            <div v-for="(entry, i) in mappingUserEntries" :key="i" class="d-flex align-center gap-2 mb-2">
              <v-text-field v-model="entry[0]" label="Key" density="compact" hide-details style="max-width: 200px" />
              <v-text-field v-model="entry[1]" label="URL" density="compact" hide-details class="flex-grow-1" />
              <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="mappingUserEntries.splice(i, 1)" />
            </div>
            <v-btn size="small" variant="text" prepend-icon="mdi-plus" @click="mappingUserEntries.push(['', ''])">添加映射</v-btn>
          </v-card-text>
        </v-card>

        <v-card class="mb-4">
          <v-card-title>其他</v-card-title>
          <v-card-text>
            <v-text-field v-model="form.AD_Help_Pica.image" label="分类页跳转LRR网页的显示图片路径" />
            <v-switch color="primary" v-model="form.SysConfig.Debug" label="调试模式" />
          </v-card-text>
        </v-card>

        <v-btn type="submit" color="primary" :loading="saving">保存</v-btn>
        <v-btn
          v-if="hasChanges"
          color="error"
          :loading="restarting"
          :disabled="saving"
          @click="handleRestart"
          class="ml-2"
        >
          立即重启
        </v-btn>
      </v-form>

      <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
        {{ snackbar.text }}
      </v-snackbar>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../api/request'

const loading = ref(true)
const saving = ref(false)
const restarting = ref(false)
const hasChanges = ref(false)
const secrets = ref({})
const snackbar = ref({ show: false, text: '', color: 'success' })

const defaultForm = () => ({
  Listen: '',
  PicaBridge_URL: '',
  JWT_KEY: '',
  lrr_Api: '',
  lrr_Api_Key: '',
  SysConfig: { Debug: false },
  db: {
    host: '',
    user: '',
    password: '',
    name: '',
    pool: { maxconnections: 10, mincached: 2, blocking: true, ping: 7, reset: true },
  },
  URL_Mappings: {},
  AD_Help_Pica: { image: '' },
})

const form = ref(defaultForm())
const SYSTEM_KEYS = ['lrr_img', 'assets']
const mappingUserEntries = ref([])

function loadConfig(config) {
  form.value.Listen = config.Listen || ''
  form.value.PicaBridge_URL = config.PicaBridge_URL || ''
  form.value.lrr_Api = config.lrr_Api || ''
  form.value.SysConfig = config.SysConfig || { Debug: false }
  form.value.URL_Mappings = config.URL_Mappings || {}
  mappingUserEntries.value = Object.entries(form.value.URL_Mappings).filter(([k]) => !SYSTEM_KEYS.includes(k))
  form.value.AD_Help_Pica = config.AD_Help_Pica || { image: '' }
  if (config.db) {
    form.value.db.host = config.db.host || ''
    form.value.db.user = config.db.user || ''
    form.value.db.name = config.db.name || ''
    form.value.db.pool = config.db.pool || { maxconnections: 10, mincached: 2, blocking: true, ping: 7, reset: true }
  }
  // Track which sensitive fields are masked
  secrets.value = {
    JWT_KEY: config.JWT_KEY === '******',
    lrr_Api_Key: config.lrr_Api_Key === '******',
    'db.password': config.db?.password === '******',
  }
}

async function fetchConfig() {
  loading.value = true
  try {
    const res = await request.get('/pbapi/config')
    loadConfig(res.data.config)
  } catch (e) {
    snackbar.value = { show: true, text: '加载配置失败', color: 'error' }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  const payload = {}

  // Only include changed top-level keys
  payload.Listen = form.value.Listen
  payload.PicaBridge_URL = form.value.PicaBridge_URL
  payload.lrr_Api = form.value.lrr_Api
  payload.SysConfig = form.value.SysConfig
  const urlMappings = { lrr_img: form.value.lrr_Api, assets: form.value.PicaBridge_URL }
  for (const [k, v] of mappingUserEntries.value) {
    if (k.trim()) urlMappings[k.trim()] = v
  }
  payload.URL_Mappings = urlMappings
  payload.AD_Help_Pica = form.value.AD_Help_Pica

  // Only send sensitive fields if user entered a value
  if (form.value.JWT_KEY) payload.JWT_KEY = form.value.JWT_KEY
  if (form.value.lrr_Api_Key) payload.lrr_Api_Key = form.value.lrr_Api_Key

  // db object - only send password if user entered a value
  const dbPayload = { ...form.value.db }
  if (!form.value.db.password) delete dbPayload.password
  payload.db = dbPayload

  try {
    const res = await request.put('/pbapi/config', payload)
    snackbar.value = { show: true, text: '保存成功', color: 'success' }
    if (res.data?.restart_required) {
      hasChanges.value = true
    }
    fetchConfig()
  } catch (e) {
    snackbar.value = { show: true, text: e.message || '保存失败', color: 'error' }
  } finally {
    saving.value = false
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
        fetchConfig()
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

onMounted(fetchConfig)
</script>
