<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card>
          <v-card-title class="text-center py-4">
            <v-icon size="48" color="primary">mdi-cog-outline</v-icon>
            <div class="text-h5 mt-2">PicaBridge 配置向导</div>
          </v-card-title>
          <v-card-text>
            <template v-if="!submitted">
              <v-stepper v-model="step" :items="['基础配置', '数据库配置', '确认提交']">
                <template #item.1>
                  <v-form ref="form1">
                    <v-text-field
                      v-model="config.PicaBridge_URL"
                      label="访问地址"
                      placeholder="https://pica.example.com"
                      :rules="[v => !!v || '必填']"
                      :error-messages="getFieldError('PicaBridge_URL')"
                    />
                    <v-text-field
                      v-model="config.JWT_KEY"
                      label="JWT 签名密钥"
                      :rules="[v => v.length >= 16 || '至少16个字符']"
                      :error-messages="getFieldError('JWT_KEY')"
                    />
                    <v-text-field
                      v-model="config.Listen"
                      label="监听地址"
                      placeholder="0.0.0.0:7777"
                      :error-messages="getFieldError('Listen')"
                    />
                    <v-text-field
                      v-model="config.lrr_Api"
                      label="LANraragi API 地址"
                      placeholder="http://192.168.1.100:3000"
                      :rules="[v => !!v || '必填']"
                      :error-messages="getFieldError('lrr_Api')"
                    />
                    <v-text-field
                      v-model="config.lrr_Api_Key"
                      label="LANraragi API Key"
                      :rules="[v => !!v || '必填']"
                      :error-messages="getFieldError('lrr_Api_Key')"
                    />
                  </v-form>
                </template>

                <template #item.2>
                  <v-form ref="form2">
                    <v-text-field
                      v-model="config.db.host"
                      label="数据库主机"
                      placeholder="127.0.0.1"
                      :rules="[v => !!v || '必填']"
                      :error-messages="getFieldError('db.host')"
                    />
                    <v-text-field
                      v-model="config.db.user"
                      label="数据库用户"
                      :rules="[v => !!v || '必填']"
                      :error-messages="getFieldError('db.user')"
                    />
                    <v-text-field
                      v-model="config.db.password"
                      label="数据库密码"
                      type="password"
                      :rules="[v => !!v || '必填']"
                      :error-messages="getFieldError('db.password')"
                    />
                    <v-text-field
                      v-model="config.db.name"
                      label="数据库名"
                      :rules="[v => !!v || '必填']"
                      :error-messages="getFieldError('db.name')"
                    />
                  </v-form>
                </template>

                <template #item.3>
                  <div class="text-center py-8">
                    <v-icon size="64" color="primary">mdi-check-circle-outline</v-icon>
                    <div class="text-h6 mt-4">提交配置</div>
                    <p class="text-medium-emphasis mt-2">确认信息填写正确，点击按钮保存配置</p>
                    <v-alert v-if="errorMsg" type="error" class="mt-4 text-left" density="compact">
                      {{ errorMsg }}
                    </v-alert>
                    <v-btn
                      color="primary"
                      size="large"
                      class="mt-6"
                      :loading="loading"
                      @click="handleSubmit"
                    >
                      提交配置
                    </v-btn>
                  </div>
                </template>
              </v-stepper>
            </template>

            <!-- 初始化完成 -->
            <template v-else>
              <div class="text-center py-8">
                <v-icon size="72" color="success">mdi-check-circle</v-icon>
                <div class="text-h5 mt-4">初始化完成</div>

                <v-alert type="info" class="mt-6 text-left" density="compact" prominent>
                  配置已写入，<strong>哔咔桥将于5秒后自动重启</strong>之后可前往管理后台进行更多配置。
                </v-alert>

                <v-card variant="tonal" class="mt-4 text-left">
                  <v-card-title class="text-subtitle-1">默认管理员账号</v-card-title>
                  <v-card-text>
                    <v-table density="compact">
                      <tbody>
                        <tr>
                          <td class="text-medium-emphasis" style="width:80px">用户名</td>
                          <td><code>Picabridge</code></td>
                        </tr>
                        <tr>
                          <td class="text-medium-emphasis">密码</td>
                          <td><code>PicaBridge233password</code></td>
                        </tr>
                      </tbody>
                    </v-table>
                    <p class="text-caption text-medium-emphasis mt-2">登录后请尽快修改默认密码</p>
                  </v-card-text>
                </v-card>

                <v-btn
                  color="primary"
                  size="large"
                  class="mt-6"
                  prepend-icon="mdi-login"
                  @click="router.push('/ui/login')"
                >
                  前往管理后台
                </v-btn>
              </div>
            </template>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '../api/request'
import { resetInitStatus } from '../router'

const router = useRouter()
const step = ref(1)
const loading = ref(false)
const submitted = ref(false)
const errorMsg = ref('')
const fieldErrors = ref({})

const config = ref({
  PicaBridge_URL: '',
  JWT_KEY: '',
  Listen: '0.0.0.0:7777',
  lrr_Api: '',
  lrr_Api_Key: '',
  db: { host: '127.0.0.1', user: '', password: '', name: '' },
})

function getFieldError(field) {
  return fieldErrors.value[field] || []
}

async function handleSubmit() {
  loading.value = true
  errorMsg.value = ''
  fieldErrors.value = {}
  try {
    await request.post('/pbapi/init', config.value)
    resetInitStatus()
    submitted.value = true
    setTimeout(() => router.push('/ui/login'), 5000)
  } catch (e) {
    if (e.data?.errors) {
      e.data.errors.forEach((err) => {
        if (!fieldErrors.value[err.field]) fieldErrors.value[err.field] = []
        fieldErrors.value[err.field].push(err.message)
      })
    }
    errorMsg.value = e.message || '提交失败'
  } finally {
    loading.value = false
  }
}
</script>
