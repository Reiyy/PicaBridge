import { useTheme } from 'vuetify'
import {
  argbFromHex,
  hexFromArgb,
  themeFromSourceColor,
  themeFromImage,
  TonalPalette,
  Hct,
} from '@material/material-color-utilities'

const STORAGE_KEY = 'picabridge-monet-theme'

const DEFAULT_SOURCE_COLOR = '#74aafb'

const SURFACE_CHROMA = 7

/**
 * 从种子色生成带色调的 neutral 色板，用于 surface-container
 */
function createTintedNeutralPalette(sourceArgb) {
  const hct = Hct.fromInt(sourceArgb)
  return TonalPalette.fromHueAndChroma(hct.hue, SURFACE_CHROMA)
}

/**
 * 亮色模式映射
 */
function mapLightColors(scheme, tintedNeutral) {
  const json = scheme.toJSON()
  const n = tintedNeutral
  return {
    primary: hexFromArgb(json.primary),
    'on-primary': hexFromArgb(json.onPrimary),
    'primary-darken-1': hexFromArgb(json.primaryContainer),
    secondary: hexFromArgb(json.secondary),
    'on-secondary': hexFromArgb(json.onSecondary),
    'secondary-darken-1': hexFromArgb(json.secondaryContainer),
    accent: hexFromArgb(json.tertiary),
    'on-accent': hexFromArgb(json.onTertiary),
    error: hexFromArgb(json.error),
    'on-error': hexFromArgb(json.onError),
    'error-darken-1': hexFromArgb(json.errorContainer),
    surface: hexFromArgb(n.tone(96)),
    'on-surface': hexFromArgb(json.onSurface),
    'surface-variant': hexFromArgb(json.surfaceVariant),
    'on-surface-variant': hexFromArgb(json.onSurfaceVariant),
    background: hexFromArgb(n.tone(96)),
    'on-background': hexFromArgb(json.onBackground),
    'outline-variant': hexFromArgb(json.outlineVariant),
    'surface-bright': hexFromArgb(n.tone(96)),
    'surface-dim': hexFromArgb(n.tone(87)),
    'surface-container-lowest': hexFromArgb(n.tone(96)),
    'surface-container-low': hexFromArgb(n.tone(94)),
    'surface-container': hexFromArgb(n.tone(92)),
    'surface-container-high': hexFromArgb(n.tone(87)),
    'surface-container-highest': hexFromArgb(n.tone(80)),
  }
}

/**
 * 暗色模式映射
 */
function mapDarkColors(scheme, tintedNeutral) {
  const json = scheme.toJSON()
  const n = tintedNeutral
  return {
    primary: hexFromArgb(json.primary),
    'on-primary': hexFromArgb(json.onPrimary),
    'primary-darken-1': hexFromArgb(json.primaryContainer),
    secondary: hexFromArgb(json.secondary),
    'on-secondary': hexFromArgb(json.onSecondary),
    'secondary-darken-1': hexFromArgb(json.secondaryContainer),
    accent: hexFromArgb(json.tertiary),
    'on-accent': hexFromArgb(json.onTertiary),
    error: hexFromArgb(json.error),
    'on-error': hexFromArgb(json.onError),
    'error-darken-1': hexFromArgb(json.errorContainer),
    surface: hexFromArgb(n.tone(12)),
    'on-surface': hexFromArgb(json.onSurface),
    'surface-variant': hexFromArgb(json.surfaceVariant),
    'on-surface-variant': hexFromArgb(json.onSurfaceVariant),
    background: hexFromArgb(n.tone(8)),
    'on-background': hexFromArgb(json.onBackground),
    'outline-variant': hexFromArgb(json.outlineVariant),
    'surface-bright': hexFromArgb(n.tone(24)),
    'surface-dim': hexFromArgb(n.tone(6)),
    'surface-container-lowest': hexFromArgb(n.tone(4)),
    'surface-container-low': hexFromArgb(n.tone(8)),
    'surface-container': hexFromArgb(n.tone(12)),
    'surface-container-high': hexFromArgb(n.tone(17)),
    'surface-container-highest': hexFromArgb(n.tone(22)),
  }
}

/**
 * 从种子颜色生成 Monet 主题
 */
export function generateThemeFromColor(hexColor) {
  const argb = argbFromHex(hexColor)
  const monet = themeFromSourceColor(argb)
  const tintedNeutral = createTintedNeutralPalette(argb)

  return {
    sourceColor: hexColor,
    light: mapLightColors(monet.schemes.light, tintedNeutral),
    dark: mapDarkColors(monet.schemes.dark, tintedNeutral),
  }
}

/**
 * 从图片元素提取主色并生成 Monet 主题
 */
export async function generateThemeFromImage(imageElement) {
  const monet = await themeFromImage(imageElement)
  const sourceColor = hexFromArgb(monet.source)
  const tintedNeutral = createTintedNeutralPalette(monet.source)

  return {
    sourceColor,
    light: mapLightColors(monet.schemes.light, tintedNeutral),
    dark: mapDarkColors(monet.schemes.dark, tintedNeutral),
  }
}

/**
 * 将生成的 Monet 主题应用到 Vuetify
 */
export function applyMonetTheme(themeData) {
  const theme = useTheme()
  theme.themes.value.light.colors = { ...theme.themes.value.light.colors, ...themeData.light }
  theme.themes.value.dark.colors = { ...theme.themes.value.dark.colors, ...themeData.dark }
}

/**
 * 从 File 对象读取图片并生成主题
 */
export function generateThemeFromImageFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = async () => {
        try {
          const themeData = await generateThemeFromImage(img)
          resolve(themeData)
        } catch (err) {
          reject(err)
        }
      }
      img.onerror = reject
      img.src = e.target.result
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export function saveThemeConfig(sourceColor, darkMode = false) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ sourceColor, darkMode }))
}

export function loadThemeConfig() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function clearThemeConfig() {
  localStorage.removeItem(STORAGE_KEY)
}

export function initTheme() {
  const saved = loadThemeConfig()
  if (saved) {
    return generateThemeFromColor(saved.sourceColor)
  }
  return generateThemeFromColor(DEFAULT_SOURCE_COLOR)
}

export { DEFAULT_SOURCE_COLOR }
