<template>
  <div class="media-shell">
    <aside class="sidebar">
      <router-link to="/media/publish" class="logo">
        <span class="logo-mark">校</span>
        <div class="logo-text">
          <strong>校园头条</strong>
          <small>创作中心</small>
        </div>
      </router-link>

      <nav class="menu">
        <router-link
          v-for="item in menus"
          :key="item.path"
          :to="item.path"
          class="menu-item"
          :class="{ active: route.path === item.path }"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-foot">
        <div class="user">
          <img :src="media.avatar" alt="avatar" />
          <div class="user-info">
            <strong>{{ media.displayName }}</strong>
            <small>{{ media.profile?.accountRole === 1 ? '审核员' : '作者' }}</small>
          </div>
        </div>
        <button class="logout" title="退出登录" @click="logout">
          <el-icon><SwitchButton /></el-icon>
        </button>
      </div>
    </aside>

    <section class="media-main">
      <header class="topbar">
        <div>
          <h1>{{ currentTitle }}</h1>
          <p>{{ currentDesc }}</p>
        </div>
        <div class="topbar-right">
          <a class="portal-link" href="/" target="_blank">
            <el-icon><View /></el-icon>
            查看用户端
          </a>
          <span class="divider"></span>
          <span class="today">{{ today }}</span>
        </div>
      </header>

      <div class="media-content">
        <router-view />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { useMediaStore } from '@/stores/media'

const route = useRoute()
const router = useRouter()
const media = useMediaStore()

const menus = computed(() => {
  if (media.profile?.accountRole === 1) {
    return [
      { path: '/media/audit', label: '审核工作台', icon: 'CircleCheck', desc: '审核作者提交的校园稿件' },
      { path: '/media/profile', label: '个人资料', icon: 'User', desc: '修改昵称、简介、头像与退出登录' }
    ]
  }
  return [
    { path: '/media/publish', label: '发布文章', icon: 'EditPen', desc: '撰写并提交校园新闻' },
    { path: '/media/content', label: '内容列表', icon: 'Document', desc: '管理我的文章与审核状态' },
    { path: '/media/material', label: '素材管理', icon: 'Picture', desc: '管理图片素材与收藏' },
    { path: '/media/profile', label: '个人资料', icon: 'User', desc: '修改昵称、简介、头像与退出登录' }
  ]
})

const current = computed(() => menus.value.find((m) => m.path === route.path) || menus.value[0])
const currentTitle = computed(() => current.value.label)
const currentDesc = computed(() => current.value.desc)
const today = dayjs().format('YYYY年MM月DD日')

async function logout() {
  await ElMessageBox.confirm('确定要退出自媒体端吗？', '退出登录', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning'
  })
  media.logout()
  router.push('/media/login')
}
</script>

<style scoped>
.media-shell {
  min-height: 100vh;
  display: flex;
  background: #f4f6fb;
}

.sidebar {
  width: 236px;
  flex-shrink: 0;
  background: var(--dark);
  color: #cdd5e4;
  display: flex;
  flex-direction: column;
  padding: 22px 16px;
  position: sticky;
  top: 0;
  height: 100vh;
}

.logo {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 4px 8px 22px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 18px;
}

.logo-mark {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 700;
  font-size: 18px;
  background: linear-gradient(135deg, #2f6bff, #7c3aed);
  box-shadow: 0 6px 16px rgba(47, 107, 255, 0.4);
}

.logo-text strong {
  color: #fff;
  display: block;
  font-size: 16px;
  line-height: 1.3;
}

.logo-text small {
  font-size: 11px;
  color: #7c879c;
  letter-spacing: 1px;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 46px;
  padding: 0 14px;
  border-radius: 11px;
  color: #aeb8c9;
  font-size: 14px;
  position: relative;
  transition: all 0.18s;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.menu-item.active {
  background: linear-gradient(90deg, rgba(47, 107, 255, 0.22), rgba(47, 107, 255, 0.05));
  color: #fff;
  font-weight: 600;
}

.menu-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 3px;
  background: #4d84ff;
}

.menu-item .el-icon {
  font-size: 19px;
}

.sidebar-foot {
  margin-top: auto;
  padding-top: 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  gap: 10px;
}

.user {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.user img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.user-info {
  min-width: 0;
}

.user-info strong {
  display: block;
  color: #fff;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-info small {
  color: #7c879c;
  font-size: 11px;
}

.logout {
  margin-left: auto;
  border: 0;
  background: rgba(255, 255, 255, 0.06);
  color: #aeb8c9;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all 0.18s;
}

.logout:hover {
  background: rgba(239, 68, 68, 0.18);
  color: #ff8a8a;
}

.media-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.topbar {
  height: 88px;
  background: #fff;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 34px;
  position: sticky;
  top: 0;
  z-index: 20;
}

.topbar h1 {
  margin: 0;
  font-size: 20px;
  letter-spacing: 0.4px;
}

.topbar p {
  margin: 3px 0 0;
  color: var(--text-3);
  font-size: 12px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: var(--text-2);
}

.portal-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--brand);
}

.divider {
  width: 1px;
  height: 18px;
  background: var(--line);
}

.today {
  color: var(--text-3);
}

.media-content {
  padding: 26px 34px 44px;
  max-width: 1280px;
  width: 100%;
}

@media (max-width: 960px) {
  .sidebar {
    width: 76px;
    padding: 18px 10px;
  }
  .logo-text,
  .menu-item span,
  .user-info {
    display: none;
  }
  .logo {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }
  .menu-item {
    justify-content: center;
    padding: 0;
  }
  .sidebar-foot {
    justify-content: center;
  }
  .logout {
    display: none;
  }
  .topbar {
    padding: 0 18px;
    height: 76px;
  }
  .topbar p,
  .today,
  .divider {
    display: none;
  }
  .media-content {
    padding: 18px 16px 36px;
  }
}
</style>
