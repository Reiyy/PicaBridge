<template>
  <div>
    <h2 class="text-h5 mb-4">关键词管理</h2>
    <v-tabs v-model="tab">
      <v-tab value="popular">常用标签</v-tab>
      <v-tab value="filter">筛选关键词</v-tab>
    </v-tabs>

    <v-skeleton-loader v-if="loading" type="card" class="mt-4" />
    <template v-else>
      <!-- Popular Keywords -->
      <template v-if="tab === 'popular'">
        <v-card class="mt-4 mb-4">
          <v-card-title>NSFW 常用标签</v-card-title>
          <v-card-text>
            <v-chip-group>
              <v-chip v-for="(kw, i) in keywords.NSFW" :key="i" closable @click:close="keywords.NSFW.splice(i, 1)">
                {{ kw }}
              </v-chip>
            </v-chip-group>
            <v-text-field
              v-model="newNsfwKeyword"
              label="新增标签"
              append-inner-icon="mdi-plus"
              @click:append-inner="addKeyword('NSFW')"
              @keyup.enter="addKeyword('NSFW')"
              density="compact"
              class="mt-2"
            />
          </v-card-text>
        </v-card>
        <v-card class="mb-4">
          <v-card-title>SFW 常用标签</v-card-title>
          <v-card-text>
            <v-chip-group>
              <v-chip v-for="(kw, i) in keywords.SFW" :key="i" closable @click:close="keywords.SFW.splice(i, 1)">
                {{ kw }}
              </v-chip>
            </v-chip-group>
            <v-text-field
              v-model="newSfwKeyword"
              label="新增标签"
              append-inner-icon="mdi-plus"
              @click:append-inner="addKeyword('SFW')"
              @keyup.enter="addKeyword('SFW')"
              density="compact"
              class="mt-2"
            />
          </v-card-text>
        </v-card>
      </template>

      <!-- Filter Keywords -->
      <template v-if="tab === 'filter'">
        <v-btn color="primary" class="mt-4 mb-2" prepend-icon="mdi-plus" @click="addFilterGroup" :disabled="Object.keys(filterKeywords).length >= 8">
          新增筛选组（最多8组）
        </v-btn>
        <v-card v-for="(items, key) in filterKeywords" :key="key" class="mb-4">
          <v-card-title class="d-flex align-center">
            第 {{ key }} 组
            <v-spacer />
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="delete filterKeywords[key]" />
          </v-card-title>
          <v-card-text>
            <v-text-field v-model="items[0]" label="显示文本" density="compact" />
            <v-text-field v-model="items[1]" label="匹配文本" density="compact" />
            <v-textarea v-if="Number(key) <= 3" v-model="items[2]" label="侧边特殊标签文本" rows="2" density="compact" hint="用 \n 分隔每行" />
          </v-card-text>
        </v-card>
      </template>

      <v-btn color="primary" class="mt-4" :loading="saving" @click="handleSave">保存</v-btn>
    </template>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">{{ snackbar.text }}</v-snackbar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../api/request'

const loading = ref(true)
const saving = ref(false)
const tab = ref('popular')
const snackbar = ref({ show: false, text: '', color: 'success' })

const keywords = ref({ NSFW: [], SFW: [] })
const filterKeywords = ref({})
const newNsfwKeyword = ref('')
const newSfwKeyword = ref('')

function addKeyword(type) {
  const val = type === 'NSFW' ? newNsfwKeyword : newSfwKeyword
  if (val.value.trim()) {
    keywords.value[type].push(val.value.trim())
    val.value = ''
  }
}

function addFilterGroup() {
  const keys = Object.keys(filterKeywords.value).map(Number)
  const next = keys.length > 0 ? Math.max(...keys) + 1 : 1
  if (next <= 8) {
    filterKeywords.value[next] = next <= 3 ? ['', '', ''] : ['', '']
  }
}

async function fetchConfig() {
  loading.value = true
  try {
    const res = await request.get('/pbapi/config')
    keywords.value = res.data.config.keywords || { NSFW: [], SFW: [] }
    filterKeywords.value = res.data.config.FilterKeywords || {}
  } catch {
    snackbar.value = { show: true, text: '加载失败', color: 'error' }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    await request.put('/pbapi/config', { keywords: keywords.value, FilterKeywords: filterKeywords.value })
    snackbar.value = { show: true, text: '保存成功', color: 'success' }
    fetchConfig()
  } catch (e) {
    snackbar.value = { show: true, text: e.message || '保存失败', color: 'error' }
  } finally {
    saving.value = false
  }
}

onMounted(fetchConfig)
</script>
