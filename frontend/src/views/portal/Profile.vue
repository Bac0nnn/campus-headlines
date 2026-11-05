<template>
  <div class="profile page">
    <div v-if="!user.isLogin" class="guest card">
      <EmptyState title="你还没有登录" description="登录后可编辑个人资料、点赞评论，收藏喜欢的校园故事">
        <el-button type="primary" round @click="goLogin">立即登录</el-button>
      </EmptyState>
    </div>

    <template v-else>
      <section class="hero card">
        <img class="hero-avatar" :src="form.avatar || user.avatar" alt="avatar" />
        <div class="hero-info">
          <h1>{{ form.nickname || user.displayName }}</h1>
          <p class="phone">{{ user.profile?.account }}</p>
          <p class="bio">{{ form.bio || '这个人很懒，还没有填写个人简介' }}</p>
        </div>
        <div class="hero-actions">
          <el-button round @click="avatarVisible = true">更换头像</el-button>
          <el-button type="danger" plain round @click="logout">退出登录</el-button>
        </div>
      </section>

      <div class="profile-grid">
        <section class="card form-card">
          <div class="section-head">
            <h2>编辑个人资料</h2>
            <span>修改后点击保存即可生效</span>
          </div>

          <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
            <el-form-item label="手机号">
              <el-input :model-value="user.profile?.account" disabled />
            </el-form-item>
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="form.nickname" maxlength="20" show-word-limit placeholder="请输入昵称" />
            </el-form-item>
            <el-form-item label="性别">
              <el-radio-group v-model="form.gender">
                <el-radio :value="0">保密</el-radio>
                <el-radio :value="1">男</el-radio>
                <el-radio :value="2">女</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="个人简介" prop="bio">
              <el-input
                v-model="form.bio"
                type="textarea"
                :rows="4"
                maxlength="200"
                show-word-limit
                placeholder="介绍一下自己，比如学院、专业、兴趣"
              />
            </el-form-item>
            <el-form-item label="头像">
              <div class="avatar-row">
                <img :src="form.avatar || user.avatar" alt="avatar" class="avatar-preview" />
                <el-button plain @click="avatarVisible = true">从头像库选择</el-button>
              </div>
            </el-form-item>

            <div class="form-actions">
              <el-button @click="resetForm">重置</el-button>
              <el-button type="primary" :loading="saving" @click="save">保存资料</el-button>
            </div>
          </el-form>
        </section>

        <aside class="side">
          <section class="card info-card">
            <h3>账号信息</h3>
            <div class="info-row"><span>账号角色</span><strong>校园用户</strong></div>
            <div class="info-row"><span>账号状态</span><strong class="ok">正常</strong></div>
            <div class="info-row"><span>注册方式</span><strong>手机号</strong></div>
          </section>

          <section class="card quick-card">
            <h3>快捷入口</h3>
            <router-link to="/" class="quick-item"><el-icon><HomeFilled /></el-icon>返回首页</router-link>
            <router-link to="/discover" class="quick-item"><el-icon><Compass /></el-icon>发现频道</router-link>
            <a class="quick-item" href="/media/login" target="_blank"><el-icon><EditPen /></el-icon>创作中心</a>
          </section>

          <section class="card danger-card">
            <h3>退出账号</h3>
            <p>退出后需要重新登录才能点赞和评论。</p>
            <el-button type="danger" plain @click="logout">退出当前账号</el-button>
          </section>
        </aside>
      </div>
    </template>

    <el-dialog v-model="avatarVisible" title="选择头像" width="520px" append-to-body>
      <div class="avatar-grid">
        <button
          v-for="item in avatars"
          :key="item"
          type="button"
          class="avatar-item"
          :class="{ active: tempAvatar === item }"
          @click="tempAvatar = item"
        >
          <img :src="item" alt="avatar" />
          <span class="check"><el-icon><Check /></el-icon></span>
        </button>
      </div>

      <div class="upload-row">
        <el-upload :show-file-list="false" accept="image/*" :http-request="customUpload">
          <el-button type="primary" plain :loading="uploading">
            <el-icon><Upload /></el-icon>
            上传本地头像
          </el-button>
        </el-upload>
        <span>支持 jpg / png / webp，≤5MB；图片二进制保存到数据库</span>
      </div>

      <template #footer>
        <el-button @click="avatarVisible = false">取消</el-button>
        <el-button type="primary" @click="applyAvatar">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import EmptyState from '@/components/EmptyState.vue'
import { updateProfile, uploadAvatar, userLogout } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const user = useUserStore()

const formRef = ref()
const saving = ref(false)
const uploading = ref(false)
const avatarVisible = ref(false)
const tempAvatar = ref('')
const avatars = Array.from({ length: 12 }, (_, index) => '/avatars/u' + (index + 1) + '.svg')

const form = reactive({
  nickname: '',
  bio: '',
  gender: 0,
  avatar: ''
})

const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度需在 2-20 个字符之间', trigger: 'blur' }
  ],
  bio: [{ max: 200, message: '个人简介不能超过 200 个字符', trigger: 'blur' }]
}

function fillForm() {
  form.nickname = user.profile?.name || ''
  form.bio = user.profile?.bio || ''
  form.gender = user.profile?.gender ?? 0
  form.avatar = user.profile?.avatar || '/avatars/u1.svg'
}

function resetForm() {
  fillForm()
  ElMessage.info('已恢复为当前保存的资料')
}

function applyAvatar() {
  form.avatar = tempAvatar.value
  avatarVisible.value = false
}

async function customUpload(options) {
  uploading.value = true
  try {
    const data = await uploadAvatar(options.file)
    user.setProfile(data)
    form.avatar = data.avatar
    tempAvatar.value = data.avatar
    ElMessage.success('头像已上传并保存到数据库')
  } finally {
    uploading.value = false
  }
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    const data = await updateProfile({
      nickname: form.nickname,
      bio: form.bio,
      gender: form.gender,
      avatar: form.avatar
    })
    user.setProfile(data)
    ElMessage.success('个人资料已更新')
  } finally {
    saving.value = false
  }
}

async function logout() {
  await ElMessageBox.confirm('确定要退出当前账号吗？', '退出登录', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    await userLogout()
  } catch (e) {
    // token 失效时也允许本地退出
  }
  user.logout()
  ElMessage.success('已退出登录')
  router.replace('/')
}

function goLogin() {
  router.push({ path: '/login', query: { redirect: '/profile' } })
}

onMounted(async () => {
  if (!user.isLogin) return
  fillForm()
  await user.refresh()
  fillForm()
  tempAvatar.value = form.avatar
})
</script>

<style scoped>
.profile {
  padding-top: 24px;
  max-width: 1000px;
}

.hero {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 28px 32px;
  background: linear-gradient(120deg, #16295a 0%, #2f6bff 70%, #7c3aed 130%);
  color: #fff;
  margin-bottom: 18px;
}

.hero-avatar {
  width: 82px;
  height: 82px;
  object-fit: cover;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.35);
  flex-shrink: 0;
}

.hero-info { flex: 1; min-width: 0; }
.hero-info h1 { margin: 0 0 4px; font-size: 24px; }
.phone { margin: 0 0 6px; font-size: 13px; opacity: 0.65; }
.bio { margin: 0; font-size: 13px; opacity: 0.85; max-width: 520px; }

.hero-actions { display: flex; gap: 10px; flex-shrink: 0; }
.hero-actions .el-button { border: 0; }

.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 18px;
  align-items: start;
}

.form-card { padding: 24px 28px 26px; }

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 18px;
}

.section-head h2 { margin: 0; font-size: 17px; }
.section-head span { color: var(--text-3); font-size: 12px; }

.avatar-row { display: flex; align-items: center; gap: 14px; }
.avatar-preview { width: 56px; height: 56px; border-radius: 50%; object-fit: cover; }

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 8px;
  border-top: 1px solid var(--line);
  margin-top: 6px;
}

.side { display: flex; flex-direction: column; gap: 16px; }

.side .card { padding: 20px 22px; }
.side h3 { margin: 0 0 14px; font-size: 15px; }

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 8px 0;
  border-top: 1px solid var(--line);
}

.info-row span { color: var(--text-3); }
.info-row strong { font-weight: 500; }
.info-row .ok { color: #16a34a; }

.quick-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 0;
  font-size: 13px;
  color: var(--text-2);
  border-top: 1px solid var(--line);
}

.quick-item .el-icon { color: var(--brand); }
.quick-item:hover { color: var(--brand); }

.danger-card p { margin: 0 0 14px; font-size: 12px; color: var(--text-3); line-height: 1.6; }

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.upload-row {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px dashed var(--line);
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.upload-row span {
  font-size: 12px;
  color: var(--text-3);
}

.avatar-item {
  position: relative;
  border: 2px solid transparent;
  border-radius: 50%;
  padding: 0;
  background: transparent;
  cursor: pointer;
}

.avatar-item img { width: 100%; border-radius: 50%; }

.avatar-item .check {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--brand);
  color: #fff;
  display: none;
  place-items: center;
  font-size: 12px;
}

.avatar-item.active { border-color: var(--brand); }
.avatar-item.active .check { display: grid; }

.guest { padding: 40px; }

@media (max-width: 900px) {
  .profile-grid { grid-template-columns: 1fr; }
  .hero { flex-wrap: wrap; padding: 22px; }
  .hero-actions { width: 100%; }
}

@media (max-width: 600px) {
  .avatar-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
