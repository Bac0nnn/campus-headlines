<template>
  <div class="login-page">
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>

    <div class="login-card">
      <router-link to="/" class="brand">
        <span class="mark">校</span>
        <div>
          <strong>校园头条</strong>
          <small>CAMPUS HEADLINES</small>
        </div>
      </router-link>

      <h1>欢迎回来</h1>
      <p class="sub">登录后即可点赞、评论，收藏你关心的校园故事</p>

      <div class="mode-tabs">
        <button :class="{ active: mode === 'code' }" @click="switchMode('code')">验证码登录</button>
        <button :class="{ active: mode === 'password' }" @click="switchMode('password')">密码登录</button>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent>
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            size="large"
            maxlength="11"
            placeholder="请输入手机号"
            :prefix-icon="Iphone"
          />
        </el-form-item>

        <el-form-item v-if="mode === 'code'" prop="code">
          <div class="code-row">
            <el-input
              v-model="form.code"
              size="large"
              maxlength="6"
              placeholder="请输入验证码"
              :prefix-icon="Message"
              @keyup.enter="submit"
            />
            <el-button size="large" class="code-btn" :disabled="counting" @click="sendCode">
              {{ counting ? countdown + 's 后重发' : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item v-else prop="password">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            show-password
            placeholder="请输入密码"
            :prefix-icon="Lock"
            @keyup.enter="submit"
          />
        </el-form-item>

        <el-button type="primary" size="large" class="submit" :loading="loading" @click="submit">
          开始使用
        </el-button>
      </el-form>

      <div class="dev-tip">
        <el-icon><InfoFilled /></el-icon>
        <span v-if="mode === 'code'">开发环境验证码 <strong>123456</strong> · 演示账号 <strong>13800138000</strong></span>
        <span v-else>演示账号 <strong>13800138000</strong> · 密码 <strong>123456</strong></span>
      </div>

      <div class="foot-links">
        <router-link to="/register">还没有账号？立即注册</router-link>
        <router-link to="/">不登录，先看看 →</router-link>
      </div>
    </div>

    <p class="copyright">© 2026 校园融媒体中心 · 记录校园每一个高光时刻</p>
  </div>
</template>

<script setup>
import { onBeforeUnmount, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Iphone, Message, Lock } from '@element-plus/icons-vue'
import { passwordLogin, phoneLogin, sendCode as sendCodeApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { useMediaStore } from '@/stores/media'

const router = useRouter()
const route = useRoute()
const user = useUserStore()
const media = useMediaStore()

const formRef = ref()
const loading = ref(false)
const counting = ref(false)
const countdown = ref(60)
const mode = ref('code')
let timer = null

const form = reactive({
  phone: '13800138000',
  code: '123456',
  password: '123456'
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '请输入 11 位手机号', trigger: 'blur' }
  ],
  code: [
    {
      validator: (rule, value, callback) => {
        if (mode.value !== 'code') return callback()
        if (!value) return callback(new Error('请输入验证码'))
        if (!/^\d{6}$/.test(value)) return callback(new Error('验证码为 6 位数字'))
        callback()
      },
      trigger: 'blur'
    }
  ],
  password: [
    {
      validator: (rule, value, callback) => {
        if (mode.value !== 'password') return callback()
        if (!value) return callback(new Error('请输入密码'))
        if (value.length < 6) return callback(new Error('密码至少 6 位'))
        callback()
      },
      trigger: 'blur'
    }
  ]
}

function switchMode(value) {
  mode.value = value
  formRef.value?.clearValidate()
}

async function sendCode() {
  if (!/^1\d{10}$/.test(form.phone)) {
    ElMessage.warning('请先输入正确的手机号')
    return
  }
  const data = await sendCodeApi(form.phone)
  ElMessage.success(data.message || '验证码已发送')
  counting.value = true
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      clearInterval(timer)
      counting.value = false
    }
  }, 1000)
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const data = mode.value === 'code'
      ? await phoneLogin({ phone: form.phone, code: form.code })
      : await passwordLogin({ phone: form.phone, password: form.password })
    if (data.userRole > 0) {
      media.setLogin(data)
      ElMessage.success('登录成功，即将进入' + (data.userRole === 2 ? '审核工作台' : '创作中心'))
      router.replace(data.userRole === 2 ? '/media/audit' : '/media/publish')
      return
    }
    user.setLogin(data)
    ElMessage.success('登录成功，' + data.name)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.replace(redirect)
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 40px 20px 70px;
  background: linear-gradient(180deg, #eef3ff 0%, #f7f9fd 45%, #ffffff 100%);
  position: relative;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.55;
  pointer-events: none;
}

.orb-1 { width: 420px; height: 420px; background: #bcd0ff; top: -140px; left: -100px; }
.orb-2 { width: 380px; height: 380px; background: #e4d6ff; right: -120px; bottom: -120px; }

.login-card {
  width: min(440px, 100%);
  background: #fff;
  border-radius: 22px;
  padding: 38px 36px 30px;
  box-shadow: 0 30px 80px rgba(23, 35, 75, 0.14);
  position: relative;
  z-index: 1;
}

.brand { display: flex; align-items: center; gap: 11px; margin-bottom: 26px; }

.mark {
  width: 42px; height: 42px; border-radius: 12px;
  display: grid; place-items: center;
  color: #fff; font-weight: 700; font-size: 20px;
  background: linear-gradient(135deg, #2f6bff, #7c3aed);
  box-shadow: 0 8px 20px rgba(47, 107, 255, 0.35);
}

.brand strong { display: block; font-size: 17px; line-height: 1.3; }
.brand small { font-size: 9px; letter-spacing: 1.6px; color: var(--text-3); }

.login-card h1 { margin: 0 0 6px; font-size: 26px; }
.sub { margin: 0 0 20px; color: var(--text-3); font-size: 13px; line-height: 1.7; }

.mode-tabs {
  display: flex;
  gap: 4px;
  background: #f2f4f8;
  padding: 4px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.mode-tabs button {
  flex: 1;
  border: 0;
  background: transparent;
  padding: 9px 0;
  border-radius: 8px;
  color: var(--text-2);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.18s;
}

.mode-tabs button.active {
  background: #fff;
  color: var(--brand);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(31, 36, 48, 0.08);
}

.code-row { display: flex; gap: 10px; width: 100%; }
.code-btn { width: 132px; flex-shrink: 0; border-radius: 10px; }

.submit { width: 100%; height: 48px; border-radius: 12px; font-size: 16px; margin-top: 6px; }

.dev-tip {
  margin-top: 18px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f4f8ff;
  color: var(--brand-dark);
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  line-height: 1.5;
}

.foot-links {
  margin-top: 22px;
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-2);
}

.foot-links a:hover { color: var(--brand); }

.copyright { position: absolute; bottom: 24px; font-size: 12px; color: var(--text-3); }

@media (max-width: 480px) {
  .login-card { padding: 28px 22px 24px; }
  .code-btn { width: 112px; }
}
</style>
