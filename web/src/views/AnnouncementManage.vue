<template>
  <div>
    <h2 class="text-h5 mb-4">公告与横幅管理</h2>
    <v-tabs v-model="tab">
      <v-tab value="announcements">公告</v-tab>
      <v-tab value="banners">横幅</v-tab>
    </v-tabs>

    <v-skeleton-loader v-if="loading" type="table" class="mt-4" />
    <template v-else>
      <v-btn color="primary" class="mt-4 mb-2" prepend-icon="mdi-plus" @click="openDialog()">
        新增{{ tab === 'announcements' ? '公告' : '横幅' }}
      </v-btn>

      <!-- Announcements -->
      <template v-if="tab === 'announcements'">
        <v-data-table :headers="announcementHeaders" :items="announcementList" class="elevation-1">
          <template #item.actions="{ item }">
            <v-btn icon="mdi-pencil" size="small" variant="text" color="primary" @click="openDialog(item)" />
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteItem('announcements', item.key)" />
          </template>
        </v-data-table>
      </template>

      <!-- Banners -->
      <template v-if="tab === 'banners'">
        <v-data-table :headers="bannerHeaders" :items="bannerList" class="elevation-1">
          <template #item.actions="{ item }">
            <v-btn icon="mdi-pencil" size="small" variant="text" color="primary" @click="openDialog(item)" />
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteItem('banners', item.key)" />
          </template>
        </v-data-table>
      </template>

      <v-btn color="primary" class="mt-4" :loading="saving" @click="handleSave">保存</v-btn>
    </template>

    <!-- Dialog -->
    <v-dialog v-model="dialog.show" max-width="600">
      <v-card>
        <v-card-title>{{ dialog.isEdit ? '编辑' : '新增' }}{{ tab === 'announcements' ? '公告' : '横幅' }}</v-card-title>
        <v-card-text>
          <template v-if="tab === 'announcements'">
            <v-text-field v-model="dialog.data.title" label="标题" />
            <v-textarea v-model="dialog.data.content" label="内容" rows="3" />
            <v-text-field v-model="dialog.data.thumb" label="主图路径" />
          </template>
          <template v-else>
            <v-text-field v-model="dialog.data.title" label="标题" />
            <v-text-field v-model="dialog.data.shortDescription" label="简介" />
            <v-text-field v-model="dialog.data.type" label="类型" />
            <v-text-field v-model="dialog.data.link" label="链接" />
            <v-text-field v-model="dialog.data.thumb" label="主图路径" />
          </template>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="dialog.show = false">取消</v-btn>
          <v-btn color="primary" @click="saveItem">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">{{ snackbar.text }}</v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import request from '../api/request'
import { useRestartStore } from '../stores/restart'

const restartStore = useRestartStore()

function generateId() {
  const chars = '0123456789abcdefghijklmnopqrstuvwxyz'
  return Array.from({ length: 24 }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
}

const loading = ref(true)
const saving = ref(false)
const tab = ref('announcements')
const snackbar = ref({ show: false, text: '', color: 'success' })

const announcements = ref({})
const banners = ref({})

const dialog = ref({
  show: false,
  isEdit: false,
  originalTitle: '',
  data: {},
})

const announcementHeaders = [
  { title: '标题', key: 'title' },
  { title: '内容', key: 'content' },
  { title: '操作', key: 'actions', sortable: false },
]

const bannerHeaders = [
  { title: '标题', key: 'title' },
  { title: '描述', key: 'shortDescription' },
  { title: '链接', key: 'link' },
  { title: '操作', key: 'actions', sortable: false },
]

const announcementList = computed(() =>
  Object.entries(announcements.value).map(([key, val]) => ({ key, ...val }))
)
const bannerList = computed(() =>
  Object.entries(banners.value).map(([key, val]) => ({ key, ...val }))
)

function openDialog(item) {
  if (item) {
    dialog.value = { show: true, isEdit: true, originalTitle: item.title, data: { ...item } }
  } else {
    const empty = tab.value === 'announcements'
      ? { id: generateId(), title: '', content: '', thumb: '' }
      : { id: generateId(), title: '', shortDescription: '', type: 'web', link: '', thumb: '' }
    dialog.value = { show: true, isEdit: false, originalTitle: '', data: empty }
  }
}

function saveItem() {
  const obj = tab.value === 'announcements' ? announcements.value : banners.value
  const key = dialog.value.data.title
  if (!key) return
  if (dialog.value.isEdit && dialog.value.originalTitle !== key) {
    delete obj[dialog.value.originalTitle]
  }
  const { key: _k, ...data } = dialog.value.data
  obj[key] = data
  dialog.value.show = false
}

function deleteItem(type, key) {
  const obj = type === 'announcements' ? announcements.value : banners.value
  delete obj[key]
}

async function fetchConfig() {
  loading.value = true
  try {
    const res = await request.get('/pbapi/config')
    announcements.value = res.data.config.announcements || {}
    banners.value = res.data.config.banners || {}
  } catch {
    snackbar.value = { show: true, text: '加载失败', color: 'error' }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const res = await request.put('/pbapi/config', { announcements: announcements.value, banners: banners.value })
    snackbar.value = { show: true, text: '保存成功', color: 'success' }
    if (res.data?.restart_required) {
      restartStore.markRestartRequired()
    }
    fetchConfig()
  } catch (e) {
    snackbar.value = { show: true, text: e.message || '保存失败', color: 'error' }
  } finally {
    saving.value = false
  }
}

onMounted(fetchConfig)
</script>
