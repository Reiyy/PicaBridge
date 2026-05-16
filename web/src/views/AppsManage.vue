<template>
  <div>
    <h2 class="text-h5 mb-4">小程序管理</h2>

    <v-skeleton-loader v-if="loading" type="table" />
    <template v-else>
      <v-btn color="primary" class="mb-2" prepend-icon="mdi-plus" @click="openDialog()">新增小程序</v-btn>

      <v-data-table :headers="headers" :items="appsList" class="elevation-1">
        <template #item.showTitleBar="{ item }">
          <v-icon :color="item.showTitleBar ? 'success' : 'grey'">
            {{ item.showTitleBar ? 'mdi-check' : 'mdi-close' }}
          </v-icon>
        </template>
        <template #item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" variant="text" color="primary" @click="openDialog(item)" />
          <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteApp(item._index)" />
        </template>
      </v-data-table>

      <v-btn color="primary" class="mt-4" :loading="saving" @click="handleSave">保存</v-btn>
    </template>

    <v-dialog v-model="dialog.show" max-width="600">
      <v-card>
        <v-card-title>{{ dialog.isEdit ? '编辑' : '新增' }}小程序</v-card-title>
        <v-card-text>
          <v-text-field v-model="dialog.data.title" label="名称" />
          <v-text-field v-model="dialog.data.url" label="链接" />
          <v-text-field v-model="dialog.data.icon" label="图标URL" />
          <v-textarea v-model="dialog.data.description" label="描述" rows="2" />
          <v-switch color="primary" v-model="dialog.data.showTitleBar" label="显示标题栏" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="dialog.show = false">取消</v-btn>
          <v-btn color="primary" @click="saveApp">确定</v-btn>
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

const loading = ref(true)
const saving = ref(false)
const snackbar = ref({ show: false, text: '', color: 'success' })
const apps = ref([])

const dialog = ref({
  show: false,
  isEdit: false,
  editIndex: -1,
  data: { title: '', url: '', icon: '', showTitleBar: false, description: '' },
})

const headers = [
  { title: '名称', key: 'title' },
  { title: '链接', key: 'url' },
  { title: '标题栏', key: 'showTitleBar' },
  { title: '操作', key: 'actions', sortable: false },
]

const appsList = computed(() => apps.value.map((app, i) => ({ ...app, _index: i })))

function openDialog(item) {
  if (item) {
    dialog.value = { show: true, isEdit: true, editIndex: item._index, data: { ...item } }
  } else {
    dialog.value = { show: true, isEdit: false, editIndex: -1, data: { title: '', url: '', icon: '', showTitleBar: false, description: '' } }
  }
}

function saveApp() {
  const { _index, ...data } = dialog.value.data
  if (dialog.value.isEdit) {
    apps.value[dialog.value.editIndex] = data
  } else {
    apps.value.push(data)
  }
  dialog.value.show = false
}

function deleteApp(index) {
  apps.value.splice(index, 1)
}

async function fetchConfig() {
  loading.value = true
  try {
    const res = await request.get('/pbapi/config')
    apps.value = res.data.config.apps || []
  } catch {
    snackbar.value = { show: true, text: '加载失败', color: 'error' }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const res = await request.put('/pbapi/config', { apps: apps.value })
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
