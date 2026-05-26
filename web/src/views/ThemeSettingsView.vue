<template>
  <div>
    <h2 class="text-h5 mb-4">主题设置</h2>

    <v-row>
      <!-- 左侧：选择方式 -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title class="text-subtitle-1">
            <v-icon icon="mdi-palette" class="mr-2" />
            选择主题颜色
          </v-card-title>
          <v-card-text>
            <!-- 种子颜色选择 -->
            <div class="mb-4">
              <div class="text-subtitle-2 mb-2">手动选择颜色</div>
              <div class="d-flex align-center gap-3">
                <input
                  type="color"
                  :value="'#' + sourceColor"
                  @input="onColorPick($event.target.value)"
                  style="width: 48px; height: 48px; border: none; cursor: pointer; border-radius: 8px;"
                />
                <v-text-field
                  v-model="sourceColor"
                  label="种子颜色 (HEX)"
                  prefix="#"
                  density="compact"
                  hide-details
                  style="max-width: 200px;"
                  @update:model-value="onHexInput"
                />
              </div>
            </div>

            <v-divider class="my-4" />

            <!-- 图片取色 -->
            <div class="mb-4">
              <div class="text-subtitle-2 mb-2">从图片取色(取色可能需要一些时间)</div>
              <div class="d-flex align-center gap-2">
                <v-btn
                  color="secondary"
                  variant="tonal"
                  prepend-icon="mdi-image"
                  :loading="imageLoading"
                  :disabled="imageLoading"
                  @click="$refs.nativeFileInput.click()"
                >
                  选择图片
                </v-btn>
                <span class="text-caption text-medium-emphasis">{{ imageFileName || '未选择文件' }}</span>
              </div>
              <input
                ref="nativeFileInput"
                type="file"
                accept="image/*"
                style="display: none;"
                @change="onNativeFileSelect"
              />
            </div>

            <v-divider class="my-4" />

            <!-- 预设颜色 -->
            <div>
              <div class="text-subtitle-2 mb-2">预设颜色</div>
              <div class="d-flex flex-wrap gap-2">
                <v-btn
                  v-for="color in presetColors"
                  :key="color.hex"
                  :color="color.hex"
                  size="small"
                  variant="flat"
                  rounded="lg"
                  @click="onColorPick(color.hex)"
                >
                  {{ color.name }}
                </v-btn>
              </div>
            </div>
          </v-card-text>
        </v-card>

        <!-- 操作按钮 -->
        <div class="d-flex gap-2">
          <v-btn color="primary" prepend-icon="mdi-content-save" @click="onSave">
            保存主题
          </v-btn>
          <v-btn variant="outlined" prepend-icon="mdi-restore" @click="onReset">
            恢复默认
          </v-btn>
        </div>
      </v-col>

      <!-- 右侧：预览 -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title class="text-subtitle-1">
            <v-icon icon="mdi-eye" class="mr-2" />
            预览
          </v-card-title>
          <v-card-text>
            <!-- 暗色/亮色切换 -->
            <div class="d-flex align-center mb-4">
              <v-icon icon="mdi-brightness-6" class="mr-2" />
              <span class="text-subtitle-2 mr-2">{{ isDark ? '暗色模式' : '亮色模式' }}</span>
              <v-spacer />
              <v-switch
                v-model="isDark"
                hide-details
                density="compact"
                @update:model-value="onDarkModeToggle"
              />
            </div>

            <v-divider class="mb-4" />

            <!-- 颜色角色预览 -->
            <div class="text-subtitle-2 mb-2">颜色角色</div>
            <div class="d-flex flex-wrap gap-2 mb-4">
              <div
                v-for="(value, key) in previewColors"
                :key="key"
                class="color-swatch"
                :style="{ backgroundColor: value }"
              >
                <span class="color-swatch-label">{{ key }}</span>
              </div>
            </div>

            <v-divider class="mb-4" />

            <!-- 组件预览 -->
            <div class="text-subtitle-2 mb-2">组件预览</div>
            <div class="d-flex flex-wrap gap-2 mb-2">
              <v-btn color="primary" size="small">Primary</v-btn>
              <v-btn color="secondary" size="small">Secondary</v-btn>
              <v-btn color="accent" size="small">Accent</v-btn>
              <v-btn color="error" size="small" variant="tonal">Error</v-btn>
            </div>
            <div class="d-flex flex-wrap gap-2 mb-2">
              <v-chip color="primary" size="small">Chip</v-chip>
              <v-chip color="secondary" variant="tonal" size="small">Tonal</v-chip>
              <v-chip color="accent" variant="outlined" size="small">Outlined</v-chip>
            </div>
            <v-alert type="info" variant="tonal" density="compact" class="mb-2">
              这是一个提示信息
            </v-alert>
            <v-text-field label="输入框预览" density="compact" hide-details />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="2000">
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTheme } from 'vuetify'
import {
  generateThemeFromColor,
  generateThemeFromImageFile,
  saveThemeConfig,
  loadThemeConfig,
  clearThemeConfig,
  DEFAULT_SOURCE_COLOR,
} from '../utils/theme'

const theme = useTheme()

const sourceColor = ref(DEFAULT_SOURCE_COLOR.replace('#', ''))
const imageFileName = ref('')
const isDark = ref(false)
const imageLoading = ref(false)
const snackbar = ref({ show: false, text: '', color: 'success' })

const presetColors = [
  { hex: '#6750A4', name: '紫' },
  { hex: '#0061A4', name: '蓝' },
  { hex: '#006E1C', name: '绿' },
  { hex: '#904D00', name: '橙' },
  { hex: '#BA1A1A', name: '红' },
  { hex: '#006874', name: '青' },
  { hex: '#4A6267', name: '灰' },
  { hex: '#8B5000', name: '棕' },
]

const previewColors = computed(() => {
  const colors = theme.current.value.colors
  return {
    primary: colors.primary,
    secondary: colors.secondary,
    accent: colors.accent,
    error: colors.error,
    'sc-lowest': colors['surface-container-lowest'] || colors.surface,
    'sc-low': colors['surface-container-low'] || colors.surface,
    'sc': colors['surface-container'] || colors.surface,
    'sc-high': colors['surface-container-high'] || colors.surface,
  }
})

/**
 * 将 Monet 生成的颜色完整替换到 Vuetify 主题
 */
function applyThemeColors(themeData) {
  const lightColors = { ...theme.themes.value.light.colors, ...themeData.light }
  const darkColors = { ...theme.themes.value.dark.colors, ...themeData.dark }
  theme.themes.value.light.colors = lightColors
  theme.themes.value.dark.colors = darkColors
}

function applySourceColor(hex) {
  const clean = hex.replace('#', '')
  sourceColor.value = clean
  const themeData = generateThemeFromColor('#' + clean)
  applyThemeColors(themeData)
}

function onColorPick(hex) {
  applySourceColor(hex)
}

function onHexInput(val) {
  const clean = val.replace('#', '')
  if (/^[0-9a-fA-F]{6}$/.test(clean)) {
    applySourceColor('#' + clean)
  }
}

async function onNativeFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return
  imageFileName.value = file.name
  imageLoading.value = true
  try {
    const themeData = await generateThemeFromImageFile(file)
    sourceColor.value = themeData.sourceColor.replace('#', '')
    applyThemeColors(themeData)
    snackbar.value = { show: true, text: '已从图片提取主题颜色', color: 'success' }
  } catch {
    snackbar.value = { show: true, text: '图片取色失败，请尝试其他图片', color: 'error' }
  } finally {
    imageLoading.value = false
    event.target.value = ''
  }
}

function onDarkModeToggle(val) {
  theme.global.name.value = val ? 'dark' : 'light'
}

function onSave() {
  saveThemeConfig('#' + sourceColor.value, isDark.value)
  snackbar.value = { show: true, text: '主题已保存', color: 'success' }
}

function onReset() {
  clearThemeConfig()
  sourceColor.value = DEFAULT_SOURCE_COLOR.replace('#', '')
  isDark.value = false
  theme.global.name.value = 'light'
  const themeData = generateThemeFromColor(DEFAULT_SOURCE_COLOR)
  applyThemeColors(themeData)
  snackbar.value = { show: true, text: '已恢复默认主题', color: 'info' }
}

onMounted(() => {
  const saved = loadThemeConfig()
  if (saved) {
    sourceColor.value = (saved.sourceColor || DEFAULT_SOURCE_COLOR).replace('#', '')
    isDark.value = !!saved.darkMode
  }
})
</script>

<style scoped>
.color-swatch {
  width: 80px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.color-swatch-label {
  font-size: 10px;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  font-weight: 500;
}
</style>
