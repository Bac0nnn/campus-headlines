<template>
  <div class="register-page">
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>

    <div class="register-card">
      <router-link to="/" class="brand">
        <span class="mark">校</span>
        <div>
          <strong>校园头条</strong>
          <small>CAMPUS HEADLINES</small>
        </div>
      </router-link>

      <h1>创建校园账号</h1>
      <p class="sub">选择你的账号类型，注册后进入对应的工作台</p>

      <div class="role-cards">
        <button
          v-for="item in roles"
          :key="item.value"
          type="button"
          class="role-card"
          :class="{ active: form.role === item.value }"
          @click="form.role = item.value"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <strong>{{ item.label }}</strong>
          <span>{{ item.desc }}</span>
        </button>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item prop="phone">
          <el-input v-model="form.phone" size="large" maxlength="11" placeholder="手机号" :prefix-icon="Iphone" />
        </el-form-item>
        <el-form-item prop="nickname">
          <el-input v-model="form.nickname" size="large" maxlength="20" placeholder="昵称（2-20 个字符）" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" size="large" type="password" show-password placeholder="密码（6-20 位）" :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input v-model="form.confirmPassword" size="large" type="password" show-password placeholder="再次输入密码" :prefix-icon="Lock" @keyup.enter="submit" />
        </el-form-item>

        <el-form-item prop="agree" class="agree-item">
          <el-checkbox v-model="form.agree">
            我已阅读并同意《校园头条用户协议》和《隐私政策》
          </el-checkbox>
        </el-form-item>

        <el-button type="primary" size="large" class="submit" :loading="loading" @click="submit">
          注册并登录
        </el-button>
      </el-form>

      <div class="foot-links">
        <span>已有账号？</span>
        <router-link to="/login">直接登录 →</router-link>
      </div>
    </div>

    <p class="copyright">© 2026 校园融媒体中心 · 记录校园每一个高光时刻</p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Iphone, Lock, User } from '@element-plus/icons-vue'
import { register } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { useMediaStore } from '@/stores/media'

const router = useRouter()
const user = useUserStore()
const media = useMediaStore()

const roles = [
  { value: 0, label: '普通用户', desc: '浏览校园新闻', icon: 'View' },
  { value: 1, label: '作者用户', desc: '发布文章并提交审核', icon: 'EditPen' },
  { value: 2, label: '审核用户', desc: '审核作者提交的稿件', icon: 'CircleCheck' }
]

const formRef = ref()
const loading = ref(false)
const form = reactive({
  phone: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  agree: false,
  role: 0
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '请输入 11 位手机号', trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度需在 2-20 个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度需在 6-20 位之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) return callback(new Error('两次输入的密码不一致'))
        callback()
      },
      trigger: 'blur'
    }
  ],
  agree: [
    {
      validator: (rule, value, callback) => {
        if (!value) return callback(new Error('请先阅读并同意用户协议'))
        callback()
      },
      trigger: 'change'
    }
  ]
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const data = await register({
      phone: form.phone,
      nickname: form.nickname,
      password: form.password,
      confirmPassword: form.confirmPassword,
      role: form.role
    })
    if (data.userRole > 0) {
      media.setLogin(data)
      ElMessage.success(data.userRole === 2 ? '审核员账号注册成功' : '作者账号注册成功')
      router.replace(data.userRole === 2 ? '/media/audit' : '/media/publish')
    } else {
      user.setLogin(data)
      ElMessage.success('注册成功，欢迎加入校园头条')
      router.replace('/')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
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
  opacity: 0.5;
  pointer-events: none;
}

.orb-1 { width: 420px; height: 420px; background: #bcd0ff; top: -140px; right: -100px; }
.orb-2 { width: 380px; height: 380px; background: #e4d6ff; left: -120px; bottom: -120px; }

.register-card {
  width: min(460px, 100%);
  background: #fff;
  border-radius: 22px;
  padding: 36px 36px 28px;
  box-shadow: 0 30px 80px rgba(23, 35, 75, 0.14);
  position: relative;
  z-index: 1;
}

.brand { display: flex; align-items: center; gap: 11px; margin-bottom: 22px; }

.mark {
  width: 42px; height: 42px; border-radius: 12px;
  display: grid; place-items: center;
  color: #fff; font-weight: 700; font-size: 20px;
  background: linear-gradient(135deg, #2f6bff, #7c3aed);
  box-shadow: 0 8px 20px rgba(47, 107, 255, 0.35);
}

.brand strong { display: block; font-size: 17px; line-height: 1.3; }
.brand small { font-size: 9px; letter-spacing: 1.6px; color: var(--text-3); }

.register-card h1 { margin: 0 0 6px; font-size: 26px; }
.sub { margin: 0 0 22px; color: var(--text-3); font-size: 13px; line-height: 1.7; }

.role-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 20px;
}

.role-card {
  border: 1px solid var(--line);
  background: #fbfcff;
  border-radius: 10px;
  padding: 12px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  cursor: pointer;
  color: var(--text-2);
  transition: all 0.18s;
}

.role-card .el-icon { font-size: 18px; color: var(--brand); }
.role-card strong { font-size: 13px; }
.role-card span { font-size: 10px; color: var(--text-3); text-align: center; line-height: 1.4; }

.role-card.active {
  border-color: var(--brand);
  background: var(--brand-soft);
  color: var(--brand-dark);
  box-shadow: 0 0 0 2px rgba(47, 107, 255, 0.12);
}

.agree-item { margin-bottom: 10px; }
.agree-item :deep(.el-checkbox__label) { font-size: 12px; color: var(--text-2); white-space: normal; line-height: 1.5; }

.submit { width: 100%; height: 48px; border-radius: 12px; font-size: 16px; margin-top: 4px; }

.foot-links { margin-top: 20px; text-align: center; font-size: 13px; color: var(--text-2); }
.foot-links a { color: var(--brand); margin-left: 4px; }

.copyright { position: absolute; bottom: 24px; font-size: 12px; color: var(--text-3); }

@media (max-width: 480px) {
  .register-card { padding: 28px 22px 24px; }
}
</style>
