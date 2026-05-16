<template>
  <div>
    <h2 class="text-h5 mb-4">用户管理</h2>

    <v-card>
      <v-card-text class="pb-0">
        <v-text-field
          v-model="search"
          label="搜索用户（昵称/账号）"
          prepend-inner-icon="mdi-magnify"
          density="compact"
          variant="outlined"
          clearable
          class="mb-2"
          @update:model-value="onSearch"
        />
      </v-card-text>

      <v-data-table-server
        :headers="headers"
        :items="users"
        :items-length="total"
        :items-per-page="pageSize"
        :page="page"
        :loading="loading"
        hover
        @update:options="onTableUpdate"
      >
        <template #item.characters="{ item }">
          <v-chip
            v-for="c in (item.characters || [])"
            :key="c"
            size="x-small"
            class="mr-1"
            variant="tonal"
            color="primary"
          >{{ c }}</v-chip>
          <span v-if="!item.characters?.length" class="text-medium-emphasis">-</span>
        </template>
        <template #item.level="{ item }">
          <v-chip color="primary" size="small" variant="tonal">Lv.{{ item.level }}</v-chip>
        </template>
        <template #item.createdate="{ item }">
          {{ formatDate(item.createdate) }}
        </template>
        <template #item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" variant="text" @click="openEdit(item)" />
          <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="openDelete(item)" />
        </template>
      </v-data-table-server>
    </v-card>

    <!-- 编辑用户对话框 -->
    <v-dialog v-model="editDialog" max-width="640" scrollable>
      <v-card>
        <v-card-title>编辑用户</v-card-title>
        <v-card-text style="max-height: 70vh;">
          <v-form ref="editFormRef">
            <v-row dense>
              <v-col cols="6">
                <v-text-field v-model="editForm.name" label="名称" density="compact" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="editForm.email" label="邮箱" density="compact" />
              </v-col>
            </v-row>
            <v-text-field
              v-model="editForm.password"
              label="密码"
              placeholder="留空则不修改"
              type="password"
              density="compact"
              class="mb-2"
            />
            <v-row dense>
              <v-col cols="6">
                <v-text-field v-model="editForm.birthday" label="生日" type="date" density="compact" />
              </v-col>
              <v-col cols="6">
                <v-select
                  v-model="editForm.gender"
                  :items="[{ title: '男', value: 'm' }, { title: '女', value: 'f' }, { title: '机器人', value: 'bot' }]"
                  item-title="title"
                  item-value="value"
                  label="性别"
                  density="compact"
                />
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="6">
                <v-text-field v-model="editForm.title" label="称号" density="compact" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="editForm.avatar" label="头像" density="compact" />
              </v-col>
            </v-row>
            <v-textarea v-model="editForm.description" label="简介" density="compact" rows="2" class="mb-2" />
            <v-row dense>
              <v-col cols="4">
                <v-text-field v-model.number="editForm.level" label="等级" type="number" density="compact" />
              </v-col>
              <v-col cols="4">
                <v-text-field v-model.number="editForm.exp" label="经验" type="number" density="compact" />
              </v-col>
              <v-col cols="4">
                <v-text-field v-model="editForm.role" label="角色" density="compact" />
              </v-col>
            </v-row>
            <v-combobox
              v-model="editForm.characters"
              label="用户组"
              multiple
              chips
              closable-chips
              density="compact"
              class="mb-2"
            />
            <v-switch
              v-model="isSfw"
              label="SFW模式"
              color="success"
              density="compact"
              hide-details
              class="mb-2"
            />

            <v-divider class="my-3" />
            <div class="text-subtitle-2 mb-2">密保问题 1</div>
            <v-text-field v-model="editForm.question1" label="问题" density="compact" class="mb-1" />
            <v-text-field v-model="editForm.answer1" label="答案" placeholder="留空则不修改" type="password" density="compact" class="mb-2" />

            <div class="text-subtitle-2 mb-2">密保问题 2</div>
            <v-text-field v-model="editForm.question2" label="问题" density="compact" class="mb-1" />
            <v-text-field v-model="editForm.answer2" label="答案" placeholder="留空则不修改" type="password" density="compact" class="mb-2" />

            <div class="text-subtitle-2 mb-2">密保问题 3</div>
            <v-text-field v-model="editForm.question3" label="问题" density="compact" class="mb-1" />
            <v-text-field v-model="editForm.answer3" label="答案" placeholder="留空则不修改" type="password" density="compact" />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="editDialog = false">取消</v-btn>
          <v-btn color="primary" :loading="editLoading" @click="saveEdit">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 删除确认对话框 -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title>确认删除</v-card-title>
        <v-card-text>
          确定要删除用户 <strong>{{ deleteTarget?.name }}</strong> 吗？此操作不可撤销。
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">取消</v-btn>
          <v-btn color="error" :loading="deleteLoading" @click="confirmDelete">删除</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">{{ snackbar.text }}</v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import request from '../api/request'

const headers = [
  { title: '昵称', key: 'name', sortable: false },
  { title: '用户组', key: 'characters', sortable: false },
  { title: '等级', key: 'level', sortable: false },
  { title: '经验', key: 'exp', sortable: false },
  { title: '称号', key: 'title', sortable: false },
  { title: '注册时间', key: 'createdate', sortable: false },
  { title: '操作', key: 'actions', sortable: false, align: 'center' },
]

const users = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const search = ref('')
let searchTimer = null

const editDialog = ref(false)
const editLoading = ref(false)
const editFormRef = ref(null)
const editForm = ref({})
const editUserId = ref(null)

const deleteDialog = ref(false)
const deleteLoading = ref(false)
const deleteTarget = ref(null)

const snackbar = ref({ show: false, text: '', color: 'success' })

// SFW mode 开关：开=sfw，关=nsfw
const isSfw = computed({
  get: () => editForm.value.mode === 'sfw',
  set: (val) => { editForm.value.mode = val ? 'sfw' : 'nsfw' },
})

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return dateStr.replace('T', ' ').substring(0, 19)
}

async function fetchUsers() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (search.value) params.search = search.value
    const res = await request.get('/pbapi/users', { params })
    users.value = res.data.users
    total.value = res.data.total
  } catch {
    snackbar.value = { show: true, text: '获取用户列表失败', color: 'error' }
  } finally {
    loading.value = false
  }
}

function onTableUpdate(options) {
  page.value = options.page
  pageSize.value = options.itemsPerPage
  fetchUsers()
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchUsers()
  }, 400)
}

async function openEdit(user) {
  editUserId.value = user.id
  try {
    const res = await request.get(`/pbapi/users/${user.id}`)
    const d = res.data
    editForm.value = {
      name: d.name || '',
      email: d.email || '',
      password: '',
      birthday: d.birthday || '',
      gender: d.gender || 'm',
      title: d.title || '',
      description: d.description || '',
      avatar: d.avatar || '',
      level: d.level ?? 1,
      exp: d.exp ?? 0,
      role: d.role || '',
      characters: Array.isArray(d.characters) ? [...d.characters] : [],
      mode: d.mode || 'nsfw',
      question1: d.question1 || '',
      answer1: '',
      question2: d.question2 || '',
      answer2: '',
      question3: d.question3 || '',
      answer3: '',
    }
    editDialog.value = true
  } catch {
    snackbar.value = { show: true, text: '获取用户详情失败', color: 'error' }
  }
}

async function saveEdit() {
  editLoading.value = true
  try {
    const payload = { ...editForm.value }
    // 空密码不提交
    if (!payload.password) delete payload.password
    // 空答案不提交
    if (!payload.answer1) delete payload.answer1
    if (!payload.answer2) delete payload.answer2
    if (!payload.answer3) delete payload.answer3
    await request.put(`/pbapi/users/${editUserId.value}`, payload)
    snackbar.value = { show: true, text: '用户信息已更新', color: 'success' }
    editDialog.value = false
    fetchUsers()
  } catch (e) {
    snackbar.value = { show: true, text: e.response?.data?.message || '更新失败', color: 'error' }
  } finally {
    editLoading.value = false
  }
}

function openDelete(user) {
  deleteTarget.value = user
  deleteDialog.value = true
}

async function confirmDelete() {
  deleteLoading.value = true
  try {
    await request.delete(`/pbapi/users/${deleteTarget.value.id}`)
    snackbar.value = { show: true, text: '用户已删除', color: 'success' }
    deleteDialog.value = false
    fetchUsers()
  } catch (e) {
    snackbar.value = { show: true, text: e.response?.data?.message || '删除失败', color: 'error' }
  } finally {
    deleteLoading.value = false
  }
}
</script>
