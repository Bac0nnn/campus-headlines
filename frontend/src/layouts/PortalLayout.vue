<template>
  <div class="portal-shell">
    <header class="site-header">
      <div class="page header-inner">
        <router-link to="/" class="brand">
          <span class="brand-mark">校</span>
          <span class="brand-text">
            <strong>校园头条</strong>
            <small>CAMPUS HEADLINES</small>
          </span>
        </router-link>

        <nav class="top-nav">
          <router-link to="/" exact-active-class="active">首页</router-link>
          <router-link to="/video" active-class="active">视频</router-link>
          <router-link to="/discover" active-class="active">发现</router-link>
        </nav>

        <div class="header-right">
          <label class="search-box">
            <el-icon><Search /></el-icon>
            <input v-model="keyword" placeholder="搜索校园新闻" @keyup.enter="doSearch" />
          </label>

          <el-dropdown v-if="user.isLogin" trigger="click" @command="onCommand">
            <div class="user-chip">
              <img :src="user.avatar" alt="avatar" />
              <span>{{ user.displayName }}</span>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <el-button v-else type="primary" round class="login-btn" @click="goLogin">登录</el-button>
        </div>
      </div>
    </header>

    <main class="site-main">
      <router-view />
    </main>

    <footer class="site-footer">
      <div class="page footer-inner">
        <div class="footer-brand">
          <span class="brand-mark small">校</span>
          <div>
            <strong>校园头条</strong>
            <p>记录校园每一个高光时刻</p>
          </div>
        </div>
        <div class="footer-links">
          <router-link to="/">首页</router-link>
          <router-link to="/discover">频道</router-link>
          <router-link to="/media/login">媒体入口</router-link>
          <a href="javascript:void(0)">关于我们</a>
        </div>
        <p class="copyright">© 2026 Campus Headlines · 校园融媒体中心</p>
      </div>
    </footer>

    <BottomTabBar />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { userLogout } from '@/api/auth'
import BottomTabBar from '@/components/BottomTabBar.vue'

const router = useRouter()
const user = useUserStore()
const keyword = ref('')

function doSearch() {
  router.push({ path: '/', query: keyword.value.trim() ? { keyword: keyword.value.trim() } : {} })
}

function goLogin() {
  router.push({ path: '/login', query: { redirect: '/' } })
}

async function onCommand(command) {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    try {
      await userLogout()
    } catch (e) {
      // 本地 token 失效时也允许退出
    }
    user.logout()
    ElMessage.success('已退出登录')
    router.push('/')
  }
}
</script>

<style scoped>
.portal-shell {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--line);
}

.header-inner {
  height: 68px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 700;
  font-size: 18px;
  background: linear-gradient(135deg, #2f6bff, #7c3aed);
  box-shadow: 0 6px 16px rgba(47, 107, 255, 0.32);
}

.brand-mark.small {
  width: 32px;
  height: 32px;
  font-size: 15px;
  border-radius: 9px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.brand-text strong {
  font-size: 18px;
  letter-spacing: 0.5px;
}

.brand-text small {
  font-size: 9px;
  letter-spacing: 1.6px;
  color: var(--text-3);
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 26px;
  font-size: 15px;
  color: var(--text-2);
}

.top-nav a {
  position: relative;
  padding: 22px 0;
  transition: color 0.2s;
}

.top-nav a:hover,
.top-nav a.active {
  color: var(--text);
  font-weight: 600;
}

.top-nav a.active::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 16px;
  transform: translateX(-50%);
  width: 18px;
  height: 3px;
  border-radius: 3px;
  background: var(--brand);
}

.header-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 14px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 236px;
  height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: #f2f5fa;
  color: var(--text-3);
  transition: all 0.2s;
}

.search-box:focus-within {
  background: #fff;
  box-shadow: 0 0 0 2px rgba(47, 107, 255, 0.18);
}

.search-box input {
  flex: 1;
  border: 0;
  outline: 0;
  background: transparent;
  font-size: 13px;
  color: var(--text);
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px 5px 5px;
  border-radius: 999px;
  background: #f2f5fa;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}

.user-chip:hover {
  background: #e9eefb;
}

.user-chip img {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.user-chip .arrow {
  font-size: 12px;
  color: var(--text-3);
}

.login-btn {
  padding: 0 20px;
}

.site-main {
  flex: 1;
  padding-bottom: 40px;
}

.site-footer {
  background: #fff;
  border-top: 1px solid var(--line);
  padding: 34px 0;
  color: var(--text-2);
}

.footer-inner {
  display: flex;
  align-items: center;
  gap: 40px;
  flex-wrap: wrap;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-brand strong {
  color: var(--text);
}

.footer-brand p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--text-3);
}

.footer-links {
  display: flex;
  gap: 26px;
  font-size: 13px;
}

.footer-links a:hover {
  color: var(--brand);
}

.copyright {
  margin: 0 0 0 auto;
  font-size: 12px;
  color: var(--text-3);
}

@media (max-width: 900px) {
  .top-nav,
  .search-box {
    display: none;
  }
  .header-inner {
    height: 60px;
    gap: 12px;
  }
  .site-footer {
    padding-bottom: 84px;
  }
  .copyright {
    margin-left: 0;
    width: 100%;
  }
}
</style>
