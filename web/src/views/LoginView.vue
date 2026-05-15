<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-8">
          <v-card-title class="text-center py-4">
            <v-icon size="48" color="primary">mdi-bridge</v-icon>
            <div class="text-h5 mt-2">PicaBridge 管理后台</div>
          </v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="email"
                label="用户名"
                prepend-inner-icon="mdi-email"
                type="email"
                required
                :error-messages="errors.email"
              />
              <v-text-field
                v-model="password"
                label="密码"
                prepend-inner-icon="mdi-lock"
                type="password"
                required
                :error-messages="errors.password"
              />
              <v-alert v-if="errorMsg" type="error" class="mb-3" density="compact">
                {{ errorMsg }}
              </v-alert>
              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                :loading="loading"
              >
                登录
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')
const errors = ref({})

async function handleLogin() {
  loading.value = true
  errorMsg.value = ''
  errors.value = {}
  try {
    await auth.login(email.value, password.value)
    router.push('/ui/')
  } catch (e) {
    errorMsg.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>
