<template>
  <div class="media-profile">
    <section class="hero-card">
      <img class="hero-avatar" :src="form.avatar || media.avatar" alt="avatar" />
      <div class="hero-info">
        <div class="name-line">
          <h1>{{ form.nickname || media.displayName }}</h1>
          <span class="role-tag">{{ isReviewer ? '审核员' : '作者' }}</span>
        </div>
        <p class="account">{{ media.profile?.account }}</p>
        <p class="bio">{{ form.bio || '这个人很懒，还没有填写个人简介' }}</p>
      </div>
      <div class="hero-actions">
        <el-button round @click="openAvatar">更换头像</el-button>
        <el-button type="danger" plain round @click="logout">退出登录</el-button>
      </div>
    </section>

    <div class="profile-grid">
      <section class="card form-card">
        <div class="section-head">
          <h2>编辑个人资料</h2>
          <span>作者与审核员共用统一账号，修改后同步到创作端</span>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-form-item label="手机号（登录名）">
            <el-input :model-value="media.profile?.account" disabled />
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
              placeholder="介绍一下自己，例如学院、职务、负责的栏目"
            />
          </el-form-item>
          <el-form-item label="头像">
            <div class="avatar-row">
              <img :src="form.avatar || media.avatar" alt="avatar" class="avatar-preview" />
              <el-button plain @click="openAvatar">从头像库选择 / 上传</el-button>
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
          <div class="info-row"><span>账号角色</span><strong>{{ isReviewer ? '审核员' : '作者' }}</strong></div>
          <div class="info-row"><span>账号状态</span><strong class="ok">正常</strong></div>
          <div class="info-row"><span>媒体号</span><strong>{{ media.profile?.name }}</strong></div>
          <div class="info-row"><span>登录方式</span><strong>手机号 + 密码</strong></div>
        </section>

        <section class="card quick-card">
          <h3>工作台入口</h3>
          <router-link v-for="item in quicks" :key="item.path" :to="item.path" class="quick-item">
            <el-icon><component :is="item.icon" /></el-icon>
            {{ item.label }}
          </router-link>
        </section>

        <section class="card danger-card">
          <h3>退出账号</h3>
          <p>退出后需要重新登录才能继续发布或审核稿件。</p>
          <el-button type="danger" plain @click="logout">退出当前账号</el-button>
        </section>
      </aside>
    </div>

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
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { updateMediaProfile, uploadMediaAvatar } from '@/api/media'
import { useMediaStore } from '@/stores/media'

const router = useRouter()
const media = useMediaStore()

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

const isReviewer = computed(() => media.profile?.accountRole === 1)
const quicks = computed(() => {
  if (isReviewer.value) {
    return [{ path: '/media/audit', label: '审核工作台', icon: 'CircleCheck' }]
  }
  return [
    { path: '/media/publish', label: '发布文章', icon: 'EditPen' },
    { path: '/media/content', label: '内容列表', icon: 'Document' },
    { path: '/media/material', label: '素材管理', icon: 'Picture' }
  ]
})

function fillForm() {
  form.nickname = media.profile?.name || ''
  form.bio = media.profile?.bio || ''
  form.gender = media.profile?.gender ?? 0
  form.avatar = media.profile?.avatar || '/avatars/m1.svg'
}

function openAvatar() {
  tempAvatar.value = form.avatar || media.avatar
  avatarVisible.value = true
}

function applyAvatar() {
  form.avatar = tempAvatar.value
  avatarVisible.value = false
}

function resetForm() {
  fillForm()
  ElMessage.info('已恢复为当前保存的资料')
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    const data = await updateMediaProfile({
      nickname: form.nickname,
      bio: form.bio,
      gender: form.gender,
      avatar: form.avatar
    })
    media.setProfile(data)
    ElMessage.success('个人资料已更新')
  } finally {
    saving.value = false
  }
}

async function customUpload(options) {
  uploading.value = true
  try {
    const data = await uploadMediaAvatar(options.file)
    media.setProfile(data)
    form.avatar = data.avatar
    tempAvatar.value = data.avatar
    ElMessage.success('头像已上传并保存到数据库')
  } finally {
    uploading.value = false
  }
}

async function logout() {
  await ElMessageBox.confirm('确定要退出创作端吗？', '退出登录', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning'
  })
  media.logout()
  ElMessage.success('已退出登录')
  router.replace('/media/login')
}

onMounted(async () => {
  if (!media.isLogin) {
    router.replace('/media/login')
    return
  }
  await media.refresh()
  if (!media.isLogin) {
    router.replace('/media/login')
    return
  }
  fillForm()
})
</script>

<style scoped>
.media-profile {
  max-width: 1180px;
}

.hero-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 28px 32px;
  border-radius: var(--radius);
  background: linear-gradient(120deg, #16295a 0%, #2f6bff 70%, #7c3aed 130%);
  color: #fff;
  margin-bottom: 18px;
  box-shadow: 0 18px 40px rgba(23, 35, 75, 0.18);
}

.hero-avatar {
  width: 82px;
  height: 82px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.35);
  object-fit: cover;
  flex-shrink: 0;
}

.hero-info { flex: 1; min-width: 0; }
.name-line { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.name-line h1 { margin: 0; font-size: 24px; }
.role-tag {
  font-size: 11px;
  padding: 2px 9px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.25);
}
.account { margin: 0 0 6px; font-size: 13px; opacity: 0.65; }
.bio { margin: 0; font-size: 13px; opacity: 0.85; max-width: 560px; }
.hero-actions { display: flex; gap: 10px; flex-shrink: 0; }
.hero-actions .el-button { border: 0; }

.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 18px;
  align-items: start;
}

.form-card { padding: 24px 28px 26px; }

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
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
  gap: 10px;
  font-size: 13px;
  padding: 8px 0;
  border-top: 1px solid var(--line);
}
.info-row span { color: var(--text-3); }
.info-row strong { font-weight: 500; text-align: right; }
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

.upload-row {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px dashed var(--line);
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.upload-row span { font-size: 12px; color: var(--text-3); }

@media (max-width: 900px) {
  .profile-grid { grid-template-columns: 1fr; }
  .hero-card { flex-wrap: wrap; padding: 22px; }
  .hero-actions { width: 100%; }
}

@media (max-width: 600px) {
  .avatar-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
