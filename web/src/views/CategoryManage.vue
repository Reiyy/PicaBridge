<template>
  <div>
    <h2 class="text-h5 mb-4">分类管理</h2>
    <v-tabs v-model="tab">
      <v-tab value="nsfw">NSFW 分类</v-tab>
      <v-tab value="sfw">SFW 分类</v-tab>
    </v-tabs>

    <v-skeleton-loader v-if="loading" type="table" class="mt-4" />
    <template v-else>
      <v-btn color="primary" class="mt-4 mb-2" prepend-icon="mdi-plus" @click="openDialog()">
        新增分类
      </v-btn>

      <v-data-table :headers="headers" :items="currentList" class="elevation-1">
        <template #item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" variant="text" color="primary" @click="openDialog(item)" />
          <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteCategory(item.key)" />
        </template>
      </v-data-table>

      <v-btn color="primary" class="mt-4" :loading="saving" @click="handleSave">
        保存
      </v-btn>
    </template>

    <!-- Edit Dialog -->
    <v-dialog v-model="dialog.show" max-width="600">
      <v-card>
        <v-card-title>{{ dialog.isEdit ? '编辑分类' : '新增分类' }}</v-card-title>
        <v-card-text>
          <v-text-field v-model="dialog.data.title" label="分类名" :rules="[v => !!v || '必填']" />
          <v-text-field v-model="dialog.data.lrr_id" label="LANraragi 分类 ID" placeholder="SET_xxx" />
          <v-select v-model="dialog.data.rule[0]" :items="[{title:'模糊',value:0},{title:'精确',value:1}]" label="匹配方式" item-title="title" item-value="value" />
          <div class="mb-2">
            <div v-for="(r, i) in dialog.data.rule.slice(1)" :key="i" class="d-flex align-center mb-1">
              <v-text-field v-model="dialog.data.rule[i + 1]" :label="`匹配标签 ${i + 1}`" placeholder="语言:汉语" density="compact" hide-details class="flex-grow-1" />
              <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="removeRule(i)" :disabled="dialog.data.rule.length <= 2" />
            </div>
            <v-btn size="small" variant="text" prepend-icon="mdi-plus" @click="addRule">添加规则</v-btn>
          </div>
          <v-textarea v-model="dialog.data.description" label="描述" rows="2" />
          <v-text-field v-model="dialog.data.thumb" label="分类图片路径" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="dialog.show = false">取消</v-btn>
          <v-btn color="primary" @click="saveCategory">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
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
const tab = ref('nsfw')
const snackbar = ref({ show: false, text: '', color: 'success' })

const categories = ref({})
const sfwCategories = ref({})

const dialog = ref({
  show: false,
  isEdit: false,
  originalTitle: '',
  data: { id: '', title: '', lrr_id: '', rule: [0, ''], description: '', thumb: '' },
})

const headers = [
  { title: '标题', key: 'title' },
  { title: 'LRR ID', key: 'lrr_id' },
  { title: '规则', key: 'ruleText' },
  { title: '操作', key: 'actions', sortable: false },
]

const currentObj = computed(() => tab.value === 'nsfw' ? categories.value : sfwCategories.value)
const currentList = computed(() =>
  Object.entries(currentObj.value).map(([key, val]) => ({
    key,
    title: val.title,
    lrr_id: val.lrr_id,
    ruleText: val.rule ? `${val.rule[0] === 0 ? '模糊' : '精确'}: ${val.rule.slice(1).filter(r => r).join(', ')}` : '',
    ...val,
  }))
)

function addRule() {
  dialog.value.data.rule.push('')
}

function removeRule(index) {
  if (dialog.value.data.rule.length > 2) {
    dialog.value.data.rule.splice(index + 1, 1)
  }
}

function openDialog(item) {
  if (item) {
    dialog.value = {
      show: true,
      isEdit: true,
      originalTitle: item.title,
      data: { ...item, rule: [...(item.rule || [0, ''])] },
    }
  } else {
    dialog.value = {
      show: true,
      isEdit: false,
      originalTitle: '',
      data: { id: generateId(), title: '', lrr_id: '', rule: [0, ''], description: '', thumb: '' },
    }
  }
}

function saveCategory() {
  const obj = tab.value === 'nsfw' ? categories.value : sfwCategories.value
  const key = dialog.value.data.title
  if (!key) return

  // 标题修改时删除旧 key
  if (dialog.value.isEdit && dialog.value.originalTitle !== key) {
    delete obj[dialog.value.originalTitle]
  }

  const { key: _k, ruleText: _r, ...data } = dialog.value.data
  obj[key] = data
  dialog.value.show = false
}

function deleteCategory(key) {
  const obj = tab.value === 'nsfw' ? categories.value : sfwCategories.value
  delete obj[key]
}

async function fetchConfig() {
  loading.value = true
  try {
    const res = await request.get('/pbapi/config')
    categories.value = res.data.config.categories || {}
    sfwCategories.value = res.data.config.SFW_categories || {}
  } catch {
    snackbar.value = { show: true, text: '加载失败', color: 'error' }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const payload = { categories: categories.value, SFW_categories: sfwCategories.value }
    const res = await request.put('/pbapi/config', payload)
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
