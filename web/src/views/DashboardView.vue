<template>
  <div>
    <h2 class="text-h5 mb-4">主页</h2>
    <v-skeleton-loader v-if="loading" type="card" />
    <template v-else>
      <!-- 欢迎信息 -->
      <v-card class="mb-4 greeting-card">
        <v-card-text class="text-h6 greeting-text">
          嗨~ {{ userName }}。{{ greetingText }}
        </v-card-text>
      </v-card>

      <!-- 统计信息 -->
      <div class="level-stats-card">
        <div class="level-stats-main">
          <!-- 左侧等级徽章卡片-->
          <div class="level-badge-wrapper">
            <div class="level-badge-inner">
              <div class="level-badge-bg"></div>
              <div class="level-badge-pattern">
                <img alt="" class="level-badge-img" src="/img/gold-bg.png" />
              </div>
              <div class="level-badge-content">
                <div class="level-name-row">
                  <v-icon
                    :icon="currentLevel.icon"
                    size="24"
                    color="#664515"
                    class="mr-1"
                  />
                  <p class="level-name">{{ currentLevel.title }}</p>
                </div>
                <div class="level-info-row">
                  <p class="level-info">共 {{ comicCount }} 本漫画</p>
                </div>
                <div class="level-info-row">
                  <p class="level-info">
                    {{
                      nextLevel
                        ? "下一级：" + nextLevel.title
                        : "已达到最高等级"
                    }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧等级进度 -->
          <div class="level-progress-card">
            <p class="level-progress-title">等级进度</p>
            <div class="level-progress-container">
              <div class="level-progress-inner">
                <div class="level-progress-wrap">
                  <div
                    class="level-progress-bar"
                    role="progressbar"
                    :aria-valuenow="progressPercent"
                    aria-valuemin="0"
                    aria-valuemax="100"
                  >
                    <div
                      class="level-progress-fill"
                      :style="{ width: Math.min(progressPercent, 100) + '%' }"
                    ></div>
                  </div>
                </div>
                <span class="level-progress-right-label">
                  <span class="level-progress-figure"
                    >{{ comicCount }} /
                    {{
                      nextLevel ? nextLevel.threshold : currentLevel.threshold
                    }}</span
                  >
                  <span class="level-progress-percent"
                    >已达成 {{ progressPercent.toFixed(1) }}%</span
                  >
                </span>
              </div>
            </div>
            <div v-if="nextLevel" class="level-progress-hint">
              距离下一级还需 {{ nextLevel.threshold - comicCount }} 本漫画
            </div>
            <div v-else class="level-progress-hint">已达到最高等级</div>
          </div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <v-card>
        <v-card-title>快捷操作</v-card-title>
        <v-card-text>
          <div class="d-flex ga-3">
            <v-btn
              color="primary"
              prepend-icon="mdi-sync"
              :loading="syncing"
              :disabled="syncing"
              @click="handleSync"
            >
              立即同步
            </v-btn>
            <v-btn
              color="warning"
              prepend-icon="mdi-restart"
              :loading="restartStore.restarting"
              :disabled="restartStore.restarting"
              @click="handleRestart"
            >
              立即重启
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </template>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import request from "../api/request";
import { useRestartStore } from "../stores/restart";

const restartStore = useRestartStore();

// 问候语
const greetings = [
  { start: 0, end: 6, text: "夜深了，嗨起来吧！" },
  { start: 6, end: 11, text: "早上好，睡个回笼觉吧~" },
  { start: 11, end: 13, text: "中午好，该吃饭了~" },
  { start: 13, end: 18, text: "下午好，睡午觉吧~" },
  { start: 18, end: 24, text: "晚上好，该起床了~" },
];

// 等级
const collectorLevels = [
  { threshold: 0, title: "纯洁无暇", icon: "mdi-book-open-variant" },
  { threshold: 100, title: "初窥门道", icon: "mdi-bookshelf" },
  { threshold: 1000, title: "渐入佳境", icon: "mdi-library" },
  { threshold: 5000, title: "炉火纯青", icon: "mdi-crown" },
  { threshold: 10000, title: "出神入化", icon: "mdi-crown-circle" },
  { threshold: 20000, title: "阅本无数", icon: "mdi-star-circle" },
];

const loading = ref(true);
const syncing = ref(false);
const comicCount = ref(0);
const userName = ref("");
const snackbar = ref({ show: false, text: "", color: "success" });

const greetingText = computed(() => {
  const hour = new Date().getHours();
  const matched = greetings.find((g) => hour >= g.start && hour < g.end);
  return matched ? matched.text : "嗨~";
});

const currentLevel = computed(() => {
  let level = collectorLevels[0];
  for (const l of collectorLevels) {
    if (comicCount.value >= l.threshold) level = l;
  }
  return level;
});

const nextLevel = computed(() => {
  for (const l of collectorLevels) {
    if (l.threshold > comicCount.value) return l;
  }
  return null;
});

const progressPercent = computed(() => {
  if (!nextLevel.value) {
    const maxThreshold = currentLevel.value.threshold;
    return maxThreshold > 0 ? (comicCount.value / maxThreshold) * 100 : 0;
  }
  const prev = currentLevel.value.threshold;
  const next = nextLevel.value.threshold;
  return ((comicCount.value - prev) / (next - prev)) * 100;
});

async function fetchStatus() {
  loading.value = true;
  try {
    const res = await request.get("/pbapi/dashboard/status");
    comicCount.value = res.data.comic_count;
    userName.value = res.data.user_name;
  } catch (e) {
    snackbar.value = { show: true, text: "获取状态信息失败", color: "error" };
  } finally {
    loading.value = false;
  }
}

async function handleSync() {
  syncing.value = true;
  try {
    const res = await request.post(
      "/comics/5822a6e3ad7ede654696e482/comments",
      {
        content: "/initcmc full all -notreport",
      },
      { timeout: 300000 }
    );
    if (res.code === 200) {
      snackbar.value = {
        show: true,
        text: res.data?.data || "执行成功",
        color: "blue",
      };
    } else {
      snackbar.value = {
        show: true,
        text: res.data?.data || res.message || "执行失败",
        color: "error",
      };
    }
  } catch (e) {
    snackbar.value = {
      show: true,
      text: e.message || "同步请求失败",
      color: "error",
    };
  } finally {
    syncing.value = false;
  }
}

async function handleRestart() {
  const result = await restartStore.handleRestart();
  if (result.status === "completed") {
    snackbar.value = { show: true, text: "服务已重启完成", color: "success" };
  } else if (result.status === "timeout") {
    snackbar.value = {
      show: true,
      text: "重启超时，请手动检查服务状态",
      color: "warning",
    };
  } else {
    snackbar.value = {
      show: true,
      text: result.message || "重启失败",
      color: "error",
    };
  }
}

onMounted(fetchStatus);
</script>

<style lang="scss" scoped>
/* ========== 问候语卡片 ========== */
.greeting-card {
  background-color: $app-bg-main !important;
  border: none;
}

.greeting-text {
  color: $app-primary !important;
  padding: 12px 16px !important;
  font-size: 1rem !important;
}

/* ========== 等级统计卡片容器 ========== */
.level-stats-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
  margin-bottom: 16px;
}

/* ========== 主内容区 ========== */
.level-stats-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

/* ========== 左侧等级徽章卡片 ========== */
.level-badge-wrapper {
  position: relative;
  display: flex;
  min-width: 0;
  flex: 1;
  border-radius: 16px;
  padding: 1px;
  background: conic-gradient(
    rgb(240, 221, 174),
    rgb(240, 221, 174) 45deg,
    rgb(195, 168, 121),
    rgb(195, 168, 121) 225deg,
    rgb(240, 221, 174) 270deg
  );
}

.level-badge-inner {
  position: relative;
  display: flex;
  min-width: 0;
  flex: 1;
  border-radius: 15px;
  overflow: hidden;
}

/* 金色渐变背景 */
.level-badge-bg {
  pointer-events: none;
  position: absolute;
  inset: 0;
  border-radius: 15px;
  background: linear-gradient(
    136.956deg,
    rgb(253, 253, 251) 0%,
    rgb(236, 211, 156) 62.581%,
    rgb(246, 236, 203) 96.421%
  );
}

.level-badge-img {
  position: absolute;
  max-width: none;
  height: 130.86%;
  width: 164.29%;
  left: -34.3%;
  top: -2.16%;
}

/* 装饰纹理 */
.level-badge-pattern {
  pointer-events: none;
  position: absolute;
  inset: 0;
  overflow: hidden;
  border-radius: 15px;
  opacity: 0.8;
}

/* 卡片内容 */
.level-badge-content {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 16px;
}

.level-name-row {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.level-name {
  font-size: 20px;
  font-weight: 600;
  line-height: 20px;
  color: #664515;
  margin: 0;
}

.level-info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

.level-info {
  font-size: 12px;
  line-height: 20px;
  color: #9a7009;
  margin: 0;
}

/* ========== 右侧等级进度卡片 ========== */
.level-progress-card {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 12px;
  min-height: 114px;
  min-width: 0;
  flex: 1;
  border-radius: 8px;
  background: #f6f6f8;
  padding: 16px;
}

.level-progress-title {
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  color: #1f2329;
  margin: 0;
}

.level-progress-container {
  container-type: inline-size;
  width: 100%;
  height: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.level-progress-inner {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  min-width: 0;
}

.level-progress-wrap {
  min-height: 6px;
  width: 100%;
}

.level-progress-bar {
  height: 10px;
  overflow: hidden;
  border-radius: 10px;
  background: #e5e6ea;
  width: 100%;
}

.level-progress-fill {
  height: 100%;
  border-radius: 10px;
  background: #3370ff;
  transition: width 0.3s ease-out;
}

.level-progress-right-label {
  display: flex;
  flex-direction: column;
}

.level-progress-figure {
  font-size: 14px;
  font-weight: 400;
  line-height: 22px;
  color: #646a73;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.level-progress-percent {
  font-size: 14px;
  font-weight: 500;
  line-height: 22px;
  color: #1f2329;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.level-progress-hint {
  font-size: 12px;
  line-height: 20px;
  color: #646a73;
  margin-top: 4px;
}

/* ========== 响应式横向排列 ========== */
@media (min-width: $app-breakpoint-md) {
  .level-stats-main {
    flex-direction: row;
    align-items: stretch;
  }

  .level-badge-wrapper {
    max-width: 360px;
  }

  .level-badge-inner {
    max-width: 360px;
  }
}

/* ========== 进度条 ========== */
@container (min-width: 36rem) {
  .level-progress-inner {
    flex-flow: row;
    align-items: center;
    gap: 12px;
  }

  .level-progress-wrap {
    flex: 1 1 auto;
    min-width: 200px;
    width: auto;
  }

  .level-progress-percent {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
  }
}

@container (min-width: 24rem) {
  .level-progress-right-label {
    flex-flow: row;
    gap: 8px;
  }
}
</style>
