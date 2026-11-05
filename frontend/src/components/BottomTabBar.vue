<template>
  <nav class="tabbar">
    <router-link
      v-for="item in items"
      :key="item.path"
      :to="item.path"
      class="tab"
      :class="{ active: isActive(item) }"
    >
      <el-icon><component :is="item.icon" /></el-icon>
      <span>{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  { path: '/', label: '主页', icon: 'HomeFilled' },
  { path: '/video', label: '视频', icon: 'VideoPlay' },
  { path: '/discover', label: '发现', icon: 'Compass' },
  { path: '/profile', label: '我的', icon: 'User' }
]

function isActive(item) {
  if (item.path === '/') return route.path === '/' || route.path.startsWith('/article')
  return route.path.startsWith(item.path)
}
</script>

<style scoped>
.tabbar {
  display: none;
}

@media (max-width: 768px) {
  .tabbar {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 40;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(14px);
    border-top: 1px solid var(--line);
    padding: 8px 0 calc(8px + env(safe-area-inset-bottom));
  }

  .tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    font-size: 11px;
    color: var(--text-3);
  }

  .tab .el-icon {
    font-size: 20px;
  }

  .tab.active {
    color: var(--brand);
    font-weight: 600;
  }
}
</style>
