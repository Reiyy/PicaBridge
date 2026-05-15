<template>
  <div>
    <h2 class="text-h5 mb-4">启动图管理</h2>
    <v-tabs v-model="tab">
      <v-tab value="general">日常启动图</v-tab>
      <v-tab value="nsfw">NSFW 启动图</v-tab>
      <v-tab value="special">节日启动图</v-tab>
    </v-tabs>

    <v-skeleton-loader v-if="loading" type="card" class="mt-4" />
    <template v-else>
      <!-- GeneralDay -->
      <template v-if="tab === 'general'">
        <v-btn color="primary" class="mt-4 mb-2" prepend-icon="mdi-plus" @click="addImage('GeneralDay')">新增</v-btn>
        <v-card v-for="(pair, key) in launchImage.GeneralDay" :key="key" class="mb-2">
          <v-card-text class="d-flex align-center gap-2">
            <v-text-field v-model="pair[0]" label="原图 URL" density="compact" hide-details class="flex-grow-1" />
            <v-text-field v-model="pair[1]" label="模糊图 URL" density="compact" hide-details class="flex-grow-1" />
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="delete launchImage.GeneralDay[key]" />
          </v-card-text>
        </v-card>
      </template>

      <!-- NSFW -->
      <template v-if="tab === 'nsfw'">
        <v-btn color="primary" class="mt-4 mb-2" prepend-icon="mdi-plus" @click="addImage('NSFW')">新增</v-btn>
        <v-card v-for="(pair, key) in launchImage.NSFW" :key="key" class="mb-2">
          <v-card-text class="d-flex align-center gap-2">
            <v-text-field v-model="pair[0]" label="原图 URL" density="compact" hide-details class="flex-grow-1" />
            <v-text-field v-model="pair[1]" label="模糊图 URL" density="compact" hide-details class="flex-grow-1" />
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="delete launchImage.NSFW[key]" />
          </v-card-text>
        </v-card>
      </template>

      <!-- SpeciallDay -->
      <template v-if="tab === 'special'">
        <v-btn color="primary" class="mt-4 mb-2" prepend-icon="mdi-plus" @click="openSpecialDialog()">新增</v-btn>
        <v-data-table :headers="specialHeaders" :items="specialList" class="elevation-1">
          <template #item.actions="{ item }">
            <v-btn icon="mdi-pencil" size="small" variant="text" color="primary" @click="openSpecialDialog(item)" />
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteSpecial(item.key)" />
          </template>
        </v-data-table>
      </template>

      <v-btn color="primary" class="mt-4" :loading="saving" @click="handleSave">保存</v-btn>
    </template>

    <!-- Special Dialog -->
    <v-dialog v-model="specialDialog.show" max-width="400">
      <v-card>
        <v-card-title>{{ specialDialog.isEdit ? '编辑' : '新增' }}节日启动图</v-card-title>
        <v-card-text>
          <v-text-field v-model="specialDialog.name" label="节日名" :rules="[v => !!v || '必填']" />
          <div class="d-flex gap-2">
            <v-select
              v-model="datePicker.month"
              :items="months"
              item-title="label"
              item-value="value"
              label="月"
              density="compact"
              hide-details
            />
            <v-select
              v-model="datePicker.day"
              :items="days"
              label="日"
              density="compact"
              hide-details
            />
          </div>
          <v-text-field v-model="specialDialog.original" label="原图 URL" />
          <v-text-field v-model="specialDialog.blur" label="模糊图 URL" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="specialDialog.show = false">取消</v-btn>
          <v-btn color="primary" @click="confirmSpecial">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">{{ snackbar.text }}</v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import request from '../api/request'

const loading = ref(true)
const saving = ref(false)
const tab = ref('general')
const snackbar = ref({ show: false, text: '', color: 'success' })

const launchImage = ref({ GeneralDay: {}, NSFW: {}, SpeciallDay: {} })
const specialDialog = ref({ show: false, isEdit: false, originalName: '', name: '', date: '', original: '', blur: '' })
const datePicker = ref({ month: null, day: null })
const months = Array.from({ length: 12 }, (_, i) => ({ label: `${i + 1} 月`, value: String(i + 1).padStart(2, '0') }))
const days = Array.from({ length: 31 }, (_, i) => String(i + 1).padStart(2, '0'))


const specialHeaders = [
  { title: '节日名', key: 'name' },
  { title: '日期', key: 'date' },
  { title: '原图', key: 'original' },
  { title: '模糊图', key: 'blur' },
  { title: '操作', key: 'actions', sortable: false },
]

const specialList = computed(() =>
  Object.entries(launchImage.value.SpeciallDay).map(([key, val]) => ({
    key,
    name: key,
    date: val[0] || '',
    original: val[1] || '',
    blur: val[2] || '',
  }))
)

function addImage(section) {
  const obj = launchImage.value[section]
  const keys = Object.keys(obj).map(k => parseInt(k.replace(/\D/g, '')) || 0)
  const next = keys.length > 0 ? Math.max(...keys) + 1 : 1
  const prefix = section === 'NSFW' ? 'n' : ''
  obj[`${prefix}${next}`] = ['', '']
}

function openSpecialDialog(item) {
  if (item) {
    specialDialog.value = { show: true, isEdit: true, originalName: item.key, name: item.name, date: item.date, original: item.original, blur: item.blur }
    datePicker.value.month = item.date ? item.date.slice(0, 2) : null
    datePicker.value.day = item.date ? item.date.slice(2, 4) : null
  } else {
    specialDialog.value = { show: true, isEdit: false, originalName: '', name: '', date: '', original: '', blur: '' }
    datePicker.value = { month: null, day: null }
  }
}

watch(() => [datePicker.value.month, datePicker.value.day], ([m, d]) => {
  if (m && d) {
    specialDialog.value.date = m + d
  }
})

function confirmSpecial() {
  const { isEdit, originalName, name, date, original, blur } = specialDialog.value
  if (!name) return
  if (isEdit && originalName !== name) {
    delete launchImage.value.SpeciallDay[originalName]
  }
  launchImage.value.SpeciallDay[name] = [date, original, blur]
  specialDialog.value.show = false
}

function deleteSpecial(key) {
  delete launchImage.value.SpeciallDay[key]
}

async function fetchConfig() {
  loading.value = true
  try {
    const res = await request.get('/pbapi/config')
    launchImage.value = res.data.config.LaunchImage || { GeneralDay: {}, NSFW: {}, SpeciallDay: {} }
  } catch {
    snackbar.value = { show: true, text: '加载失败', color: 'error' }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    await request.put('/pbapi/config', { LaunchImage: launchImage.value })
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
