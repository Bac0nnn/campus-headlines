<template>
  <div class="login-page">
    <section class="brand-side">
      <div class="brand-top">
        <span class="mark">校</span>
        <span>校园头条 · 创作中心</span>
      </div>

      <div class="brand-copy">
        <p class="eyebrow">CAMPUS MEDIA CENTER</p>
        <h1>让每一条校园新闻<br />都被看见</h1>
        <p class="desc">素材管理 · 富文本创作 · 内容审核 · 数据追踪</p>
        <ul class="features">
          <li><span class="dot"></span> 一站式素材库，图片随取随用</li>
          <li><span class="dot"></span> 智能编辑器，排版像写文档一样简单</li>
          <li><span class="dot"></span> 提交审核后自动流转，发布即触达全校</li>
        </ul>
      </div>

      <div class="brand-foot">© 2026 校园融媒体中心 · Campus Headlines</div>

      <span class="glow glow-1"></span>
      <span class="glow glow-2"></span>
      <span class="grid-mask"></span>
    </section>

    <section class="form-side">
      <div class="form-card">
        <div class="mobile-brand">
          <span class="mark">校</span>
          <span>校园头条</span>
        </div>
        <h2>作者 / 审核员登录</h2>
        <p class="sub">作者发布稿件，审核员审核稿件，登录后自动进入对应工作台</p>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              size="large"
              placeholder="请输入手机号或用户名"
              :prefix-icon="User"
              autocomplete="username"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              size="large"
              type="password"
              show-password
              placeholder="请输入密码"
              :prefix-icon="Lock"
              autocomplete="current-password"
              @keyup.enter="submit"
            />
          </el-form-item>
          <el-button type="primary" size="large" class="submit" :loading="loading" @click="submit">
            登录创作中心
          </el-button>
        </el-form>

        <div class="demo-account">
          <el-icon><InfoFilled /></el-icon>
          <span>
            作者 <strong>13900000002</strong> / 123456
            <br />
            审核 <strong>13900000001</strong> / 123456
          </span>
        </div>

        <div class="links">
          <router-link to="/login">普通用户登录</router-link>
          <router-link to="/register">注册作者 / 审核员</router-link>
        </div>

        <div class="links secondary">
          <router-link to="/">← 返回用户端</router-link>
          <a href="javascript:void(0)" @click="showHelp">忘记密码？</a>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { mediaLogin } from '@/api/media'
import { useMediaStore } from '@/stores/media'

const router = useRouter()
const route = useRoute()
const media = useMediaStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '13900000002', password: '123456' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const data = await mediaLogin(form)
    media.setLogin(data)
    ElMessage.success('欢迎回来，' + data.name)
    const fallback = data.accountRole === 1 ? '/media/audit' : '/media/publish'
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : fallback
    router.replace(redirect)
  } finally {
    loading.value = false
  }
}

function showHelp() {
  ElMessageBox.alert('请联系校园融媒体中心管理员重置密码，或在数据库中更新 wm_user 表。', '忘记密码', {
    confirmButtonText: '知道了'
  })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  background: #fff;
}

.brand-side {
  position: relative;
  overflow: hidden;
  padding: 44px 56px;
  display: flex;
  flex-direction: column;
  color: #fff;
  background: radial-gradient(circle at 18% 12%, #2f6bff 0%, #1b2a5e 46%, #101528 100%);
}

.brand-top {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  letter-spacing: 0.4px;
  z-index: 2;
}

.mark {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.24);
  font-weight: 700;
}

.brand-copy {
  margin: auto 0;
  z-index: 2;
  max-width: 520px;
}

.eyebrow {
  letter-spacing: 5px;
  font-size: 11px;
  opacity: 0.6;
  margin: 0 0 18px;
}

.brand-copy h1 {
  font-size: 44px;
  line-height: 1.28;
  margin: 0 0 20px;
  font-weight: 700;
  letter-spacing: 1px;
}

.desc {
  font-size: 15px;
  opacity: 0.72;
  margin: 0 0 30px;
}

.features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  font-size: 14px;
  opacity: 0.86;
}

.features li {
  display: flex;
  align-items: center;
  gap: 10px;
}

.features .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #7ea5ff;
  box-shadow: 0 0 0 4px rgba(126, 165, 255, 0.16);
}

.brand-foot {
  font-size: 12px;
  opacity: 0.45;
  z-index: 2;
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(10px);
}

.glow-1 {
  width: 460px;
  height: 460px;
  right: -160px;
  top: -120px;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.55), transparent 68%);
}

.glow-2 {
  width: 380px;
  height: 380px;
  left: -120px;
  bottom: -140px;
  background: radial-gradient(circle, rgba(47, 107, 255, 0.55), transparent 68%);
}

.grid-mask {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255, 255, 255, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.045) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(circle at 40% 45%, #000 20%, transparent 75%);
}

.form-side {
  display: grid;
  place-items: center;
  padding: 40px;
  background: #fbfcfe;
}

.form-card {
  width: min(400px, 100%);
  background: #fff;
  border-radius: 20px;
  padding: 40px 36px 30px;
  box-shadow: 0 24px 70px rgba(23, 35, 75, 0.1);
}

.mobile-brand {
  display: none;
}

.form-card h2 {
  margin: 0 0 6px;
  font-size: 24px;
}

.sub {
  margin: 0 0 26px;
  color: var(--text-3);
  font-size: 13px;
}

.submit {
  width: 100%;
  height: 46px;
  border-radius: 12px;
  font-size: 15px;
  margin-top: 4px;
}

.demo-account span {
  line-height: 1.7;
}

.demo-account {
  margin-top: 20px;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--brand-soft);
  color: var(--brand-dark);
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.links {
  margin-top: 18px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-3);
}

.links.secondary {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--line);
}

.links a:hover {
  color: var(--brand);
}

@media (max-width: 900px) {
  .login-page {
    grid-template-columns: 1fr;
  }
  .brand-side {
    display: none;
  }
  .form-side {
    padding: 24px;
    background: linear-gradient(180deg, #eef3ff, #fbfcfe 40%);
  }
  .form-card {
    padding: 30px 24px;
  }
  .mobile-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 22px;
    font-weight: 600;
  }
  .mobile-brand .mark {
    background: linear-gradient(135deg, #2f6bff, #7c3aed);
    border: 0;
  }
}
</style>
