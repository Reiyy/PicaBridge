<template>
  <v-app class="app-layout">
    <!-- 顶部导航栏 - 透明背景，浮在蓝色背景上 -->
    <div class="app-header">
      <!-- 三横线按钮 - 控制侧边栏展开/收起 -->
      <button
        class="app-header__hamburger"
        :aria-label="navExpanded ? '收起导航菜单' : '展开导航菜单'"
        @click="navExpanded = !navExpanded"
      >
        <v-icon size="22">mdi-menu</v-icon>
      </button>

      <!-- 项目 Logo -->
      <router-link to="/ui" class="app-header__logo">
        <img
          src="/img/picabridge.png"
          alt="Logo"
          class="app-header__logo-img"
        />
        <span class="app-header__logo-text">{{ appName }}</span>
      </router-link>

      <div class="app-header__spacer" />

      <div class="app-header__actions">
        <!-- 重启按钮（仅在需要重启时显示） -->
        <v-btn
          v-if="restartStore.restartRequired"
          color="error"
          size="small"
          variant="outlined"
          :loading="restartStore.restarting"
          :disabled="restartStore.restarting"
          prepend-icon="mdi-restart"
          class="restart-btn"
          @click="onRestart"
        >
          立即重启
        </v-btn>

        <!-- 设置与实用工具 -->
        <v-menu location="bottom end">
          <template #activator="{ props: menuProps }">
            <button class="app-header__action-btn" v-bind="menuProps">
              <v-icon size="20">mdi-dots-vertical</v-icon>
            </button>
          </template>
          <v-card class="app-header__settings-card" elevation="0" role="menu">
            <div class="app-header__settings-section">
              <a
                :href="lrrApi || '#'"
                target="_blank"
                class="app-header__settings-item"
                role="menuitem"
                :class="{ 'app-header__settings-item--disabled': !lrrApi }"
              >
                <span class="app-header__settings-item-icon"></span>
                <span class="app-header__settings-item-label app-text-link"
                  >前往LRR</span
                >
                <v-icon size="14" class="app-header__external-icon"
                  >mdi-open-in-new</v-icon
                >
              </a>
            </div>
            <div
              class="app-header__settings-section app-header__settings-section--last"
            >
              <a
                href="https://github.com/Reiyy/PicaBridge"
                target="_blank"
                class="app-header__settings-item"
                role="menuitem"
              >
                <span class="app-header__settings-item-icon"></span>
                <span class="app-header__settings-item-label app-text-link"
                  >浏览文档</span
                >
                <v-icon size="14" class="app-header__external-icon"
                  >mdi-open-in-new</v-icon
                >
              </a>
            </div>
          </v-card>
        </v-menu>

        <!-- 用户头像 -->
        <v-menu location="bottom end">
          <template #activator="{ props: menuProps }">
            <button class="app-header__avatar-btn" v-bind="menuProps">
              <img
                v-if="userAvatar"
                :src="userAvatar"
                class="app-header__avatar-img"
              />
              <div v-else class="app-header__avatar">{{ userInitials }}</div>
            </button>
          </template>
          <v-card class="app-header__user-card" elevation="0">
            <div class="app-header__user-info">
              <img
                v-if="userAvatar"
                :src="userAvatar"
                class="app-header__user-avatar-lg-img"
              />
              <div v-else class="app-header__user-avatar-lg">
                {{ userInitials }}
              </div>
              <div class="app-header__user-details">
                <div class="app-header__user-name">{{ userName }}</div>
                <div v-if="userTitle" class="app-header__user-title">
                  {{ userTitle }}
                </div>
              </div>
            </div>
            <div class="app-header__user-actions">
              <button class="app-header__user-action-btn" @click="handleLogout">
                退出
              </button>
            </div>
          </v-card>
        </v-menu>
      </div>
    </div>

    <!-- 主区域：侧边栏 + 白色内容区 -->
    <div class="app-main">
      <nav
        class="app-sidebar"
        :class="{ 'app-sidebar--collapsed': !navExpanded }"
      >
        <div class="app-sidebar__body">
          <router-link
            v-for="item in menuItems"
            :key="item.title"
            :to="item.to"
            class="app-sidebar__item"
            :class="{ 'app-sidebar__item--active': isActive(item.to) }"
            :title="!navExpanded ? item.title : undefined"
          >
            <v-icon size="20" class="app-sidebar__item-icon">{{
              item.icon
            }}</v-icon>
            <span v-if="navExpanded" class="app-sidebar__item-text">{{
              item.title
            }}</span>
          </router-link>

          <div
            v-for="group in menuGroups"
            :key="group.title"
            class="app-sidebar__group"
          >
            <button
              class="app-sidebar__group-header"
              :class="{
                'app-sidebar__group-header--open': isGroupOpen(group.title),
              }"
              :title="!navExpanded ? group.title : undefined"
              @click="toggleGroup(group.title)"
            >
              <v-icon size="20" class="app-sidebar__item-icon">{{
                group.icon
              }}</v-icon>
              <span v-if="navExpanded" class="app-sidebar__item-text">{{
                group.title
              }}</span>
              <v-icon
                v-if="navExpanded"
                size="18"
                class="app-sidebar__group-arrow"
                :class="{
                  'app-sidebar__group-arrow--open': isGroupOpen(group.title),
                }"
                >mdi-chevron-down</v-icon
              >
            </button>
            <transition name="app-expand">
              <div
                v-if="navExpanded && isGroupOpen(group.title)"
                class="app-sidebar__group-items"
              >
                <router-link
                  v-for="child in group.items"
                  :key="child.title"
                  :to="child.to"
                  class="app-sidebar__subitem"
                  :class="{
                    'app-sidebar__subitem--active': isActive(child.to),
                  }"
                >
                  <v-icon
                    v-if="child.icon"
                    size="18"
                    class="app-sidebar__subitem-icon"
                    >{{ child.icon }}</v-icon
                  >
                  <span class="app-sidebar__subitem-text">{{
                    child.title
                  }}</span>
                </router-link>
              </div>
            </transition>
          </div>
        </div>
      </nav>

      <div class="app-container">
        <div class="app-scroll">
          <div class="app-content">
            <slot />
          </div>
        </div>
      </div>
    </div>

    <!-- 全局消息提示 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useRestartStore } from "../stores/restart";
import request from "../api/request";

const props = defineProps({
  appName: { type: String, default: "PicaBridge" },
  userName: { type: String, default: "用户" },
  userEmail: { type: String, default: "" },
  userAvatar: { type: String, default: "" },
  userTitle: { type: String, default: "" },
  menuItems: { type: Array, default: () => [] },
  menuGroups: { type: Array, default: () => [] },
});

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const restartStore = useRestartStore();

const navExpanded = ref(false);
const openGroups = ref([]);
const snackbar = ref({ show: false, text: "", color: "success" });
const lrrApi = ref("");

onMounted(async () => {
  try {
    const res = await request.get("/pbapi/config");
    if (res.code === 200 && res.data?.config?.lrr_Api) {
      lrrApi.value = res.data.config.lrr_Api;
    }
  } catch (e) {
    console.error("获取配置失败:", e);
  }
});

const userInitials = computed(() => {
  const parts = props.userName.split(" ");
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return props.userName.substring(0, 2).toUpperCase();
});

const isActive = (path) => {
  return route.path === path;
};

const toggleGroup = (title) => {
  if (!navExpanded.value) {
    navExpanded.value = true;
    if (!openGroups.value.includes(title)) {
      openGroups.value.push(title);
    }
    return;
  }
  const index = openGroups.value.indexOf(title);
  if (index === -1) {
    openGroups.value.push(title);
  } else {
    openGroups.value.splice(index, 1);
  }
};

const isGroupOpen = (title) => {
  return openGroups.value.includes(title);
};

async function onRestart() {
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

function handleLogout() {
  auth.logout();
  router.push("/ui/login");
}
</script>

<style lang="scss" scoped>
.app-layout {
  font-family: $app-font-body;
  background-color: $app-bg-main !important;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

// 重启按钮脉冲动画
.restart-btn {
  border: 2px solid rgb(var(--v-theme-error)) !important;
  animation: restart-pulse 1.5s ease-in-out infinite;
  margin-right: 4px;
}

@keyframes restart-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

// ============================================
// 顶栏
// ============================================
.app-header {
  display: flex;
  align-items: center;
  height: $app-nav-height;
  padding: 0 8px;
  background-color: transparent;
  position: sticky;
  top: 0;
  z-index: 100;

  &__hamburger {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: none;
    background: none;
    border-radius: 50%;
    cursor: pointer;
    color: $app-text-secondary;
    transition: background-color 0.2s;
    flex-shrink: 0;

    &:hover {
      background-color: rgba(0, 0, 0, 0.04);
    }
  }

  &__logo {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: $app-text-primary;
    margin-left: 4px;
    padding: 4px 8px;
    border-radius: 4px;
    transition: background-color 0.2s;

    &:hover {
      background-color: rgba(0, 0, 0, 0.04);
    }
  }

  &__logo-img {
    width: 24px;
    height: 24px;
    object-fit: contain;
    border-radius: 6px;
  }

  &__logo-text {
    font-family: $app-font-primary;
    font-size: 18px;
    font-weight: 500;
  }

  &__spacer {
    flex: 1;
  }

  &__search {
    display: flex;
    align-items: center;
    height: $app-search-height;
    background-color: $app-bg-search;
    border-radius: $app-search-radius;
    padding: 0 12px;
    min-width: 200px;
    max-width: 600px;
    flex: 1;
    margin: 0 16px;
    transition: background-color 0.2s;

    &:focus-within {
      background-color: $app-bg-surface;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
    }
  }

  &__search-icon {
    color: $app-text-secondary;
    margin-right: 8px;
    flex-shrink: 0;
  }

  &__search-input {
    border: none;
    outline: none;
    background: transparent;
    font-family: $app-font-body;
    font-size: 14px;
    color: $app-text-primary;
    width: 100%;
    line-height: 20px;

    &::placeholder {
      color: $app-text-secondary;
      opacity: 1;
    }
  }

  &__actions {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  &__action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: none;
    background: none;
    border-radius: 50%;
    cursor: pointer;
    color: $app-text-secondary;
    transition: background-color 0.2s;
    position: relative;

    &:hover {
      background-color: $app-bg-hover;
    }
  }

  &__avatar-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    background: none;
    border-radius: 50%;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background-color: $app-bg-hover;
    }
  }

  &__avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: $app-primary;
    color: white;
    font-size: 13px;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__avatar-img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
  }

  // ---- 下拉卡片 ----
  &__user-card {
    border-radius: 0 !important;
    border: 1px solid $app-border-hairline !important;
    box-shadow: $app-shadow-2 !important;
    background-color: $app-bg-main !important;
  }

  // ---- 设置菜单 ----
  &__settings-card {
    border-radius: 12px !important;
    border: none !important;
    box-shadow: $app-shadow-2 !important;
    background-color: $app-bg-main !important;
    padding: 0 !important;
    width: auto;
    min-width: 172px;
    overflow: hidden;
  }

  &__settings-section {
    padding: 8px 0;
    border-bottom: 0.8px solid $app-border-hairline;

    &--last {
      border-bottom: none;
    }
  }

  &__settings-item {
    display: flex;
    align-items: center;
    width: 100%;
    height: 32px;
    padding: 6px 16px;
    border: none;
    background: transparent;
    cursor: pointer;
    text-align: left;
    transition: background-color 0.15s;
    position: relative;
    font-family: $app-font-body;
    box-sizing: border-box;
    text-decoration: none;
    color: inherit;

    &:hover {
      background-color: rgba(0, 0, 0, 0.04);
    }

    &--has-note {
      flex-direction: column;
      align-items: flex-start;
      height: auto;
      padding: 6px 16px;
    }

    &--disabled {
      opacity: 0.5;
      cursor: not-allowed;
      pointer-events: none;
    }
  }

  &__settings-item-main {
    display: flex;
    align-items: center;
    width: 100%;
    height: 20px;
  }

  &__settings-item-icon {
    display: inline-block;
    width: 0;
    margin-right: 0;
    flex-shrink: 0;
  }

  &__settings-item-label {
    font-size: 14px;
    font-weight: 400;
    font-family: $app-font-body;
    color: $app-text-dark;
    line-height: 20px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__settings-item-note {
    font-size: 14px;
    color: $app-text-variant;
    line-height: 20px;
    margin-top: 0;
    padding: 0;
  }

  &__external-icon {
    color: $app-text-secondary !important;
    margin-left: auto;
  }

  // ---- 用户卡片 ----
  &__user-info {
    display: flex;
    align-items: flex-start;
    gap: 20px;
    margin: 20px;
    height: 96px;
  }

  &__user-avatar-lg {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    background-color: $app-primary;
    color: white;
    font-size: 36px;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__user-avatar-lg-img {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }

  &__user-details {
    min-width: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
  }

  &__user-name {
    font-size: 18px;
    font-weight: 700;
    font-family: $app-font-body;
    color: $app-text-dark;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 24px;
  }

  &__user-email {
    font-size: 14px;
    font-weight: 500;
    font-family: $app-font-body;
    color: $app-text-variant;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 20px;
  }

  &__user-title {
    font-size: 14px;
    color: $app-text-secondary;
    margin-top: 4px;
  }

  &__user-legal-item {
    display: flex;
    align-items: center;
    height: 32px;
    padding: 0 16px;
    font-size: 14px;
    font-weight: 400;
    font-family: $app-font-body;
    color: $app-text-dark;
    text-decoration: none;
    line-height: 20px;
    transition: background-color 0.15s;

    &:hover {
      background-color: rgba(0, 0, 0, 0.04);
    }
  }

  &__user-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 0 16px;
    height: 53px;
    background-color: $app-bg-user-actions;
    border-top: 0.8px solid $app-border-hairline;
  }

  &__user-action-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 32px;
    padding: 0 12px;
    font-size: 14px;
    font-weight: 500;
    font-family: $app-font-primary;
    color: $app-text-action;
    background: transparent;
    border: 0.8px solid $app-border-action;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.15s;
    text-decoration: none;

    &:hover {
      background-color: $app-bg-hover;
    }
  }
}

// 主区域 - 侧边栏 + 白色内容区并排
// 两者都在浅蓝色背景上
.app-main {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

// 侧边栏 - 坐在浅蓝色背景上，无白色底
.app-sidebar {
  width: 200px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background-color: transparent;
  padding-top: 8px;
  transition: width 0.2s ease;
  overflow: hidden;

  &--collapsed {
    width: 48px;
    padding-top: 8px;

    .app-sidebar__item,
    .app-sidebar__group-header {
      justify-content: center;
      padding: 0;
      margin: 1px 4px;
    }

    .app-sidebar__item-icon {
      margin-right: 0;
    }

    .app-sidebar__group {
      margin-top: 0;
    }
  }

  &__body {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 0;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background-color: rgba(0, 0, 0, 0.12);
      border-radius: 2px;
    }
  }

  &__item {
    display: flex;
    align-items: center;
    height: 36px;
    padding: 0 12px;
    margin: 0 4px;
    border-radius: 4px;
    text-decoration: none;
    color: $app-text-dark;
    font-size: 14px;
    font-weight: 500;
    font-family: $app-font-primary;
    transition: background-color 0.15s;
    white-space: nowrap;
    overflow: hidden;
    position: relative;

    &:hover {
      background-color: rgba(0, 0, 0, 0.04);
    }

    &--active {
      background-color: $app-bg-active;
      border-radius: 0 12px 12px 0;
      color: $app-text-dark;

      .app-sidebar__item-icon {
        color: $app-text-dark;
      }
    }
  }

  &__item-icon {
    flex-shrink: 0;
    color: $app-text-secondary;
    margin-right: 12px;
  }

  &__item-text {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__group {
    margin-top: 4px;
  }

  &__group-header {
    display: flex;
    align-items: center;
    height: 36px;
    padding: 0 12px;
    margin: 0 4px;
    border-radius: 4px;
    border: none;
    background: none;
    cursor: pointer;
    color: $app-text-dark;
    font-size: 14px;
    font-weight: 500;
    font-family: $app-font-primary;
    width: calc(100% - 8px);
    transition: background-color 0.15s;
    text-align: left;

    &:hover {
      background-color: rgba(0, 0, 0, 0.04);
    }
  }

  &__group-arrow {
    color: $app-text-secondary;
    transition: transform 0.2s ease;
    flex-shrink: 0;
    margin-left: auto;

    &--open {
      transform: rotate(180deg);
    }
  }

  &__group-items {
    padding: 2px 0;
  }

  &__subitem {
    display: flex;
    align-items: center;
    height: 36px;
    padding: 0 12px 0 44px;
    margin: 0 4px;
    border-radius: 4px;
    text-decoration: none;
    color: $app-text-dark;
    font-size: 14px;
    font-weight: 400;
    font-family: $app-font-body;
    transition: background-color 0.15s;
    white-space: nowrap;
    overflow: hidden;
    position: relative;

    &:hover {
      background-color: rgba(0, 0, 0, 0.04);
    }

    &--active {
      background-color: $app-bg-active;
      border-radius: 0 12px 12px 0;
      color: $app-text-dark;
      font-weight: 500;
    }
  }

  &__subitem-icon {
    flex-shrink: 0;
    color: $app-text-secondary;
    margin-right: 8px;
  }

  &__subitem-text {
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

// 白色内容容器 - 占据剩余空间，顶部圆角
.app-container {
  flex: 1;
  min-width: 0;
  max-width: none;
  background-color: $app-bg-surface;
  border-radius: 20px 20px 0 0;
  margin: 4px 16px 0 0;
  padding: 0;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.app-scroll {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;

  &::-webkit-scrollbar {
    width: 16px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
    border-left: 4px solid transparent;
  }

  &::-webkit-scrollbar-track:hover {
    background-color: rgba(0, 0, 0, 0.05);
    box-shadow: inset 1px 0 0 rgba(0, 0, 0, 0.1);
  }

  &::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.2);
    background-clip: padding-box;
    border: 1px solid transparent;
    border-left-width: 6px;
    min-height: 28px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background-color: rgba(0, 0, 0, 0.4);
  }

  &::-webkit-scrollbar-corner {
    background: transparent;
  }
}

.app-content {
  max-width: none;
  margin: 0;
  padding: 24px;
}

// 展开/收起动画
.app-expand-enter-active {
  transition: all 0.2s ease-out;
  overflow: hidden;
}

.app-expand-leave-active {
  transition: all 0.15s ease-in;
  overflow: hidden;
}

.app-expand-enter-from,
.app-expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.app-expand-enter-to,
.app-expand-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
