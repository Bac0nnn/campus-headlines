<template>
  <div class="publish-page">
    <PageHeader title="发布文章" subtitle="写好一篇校园新闻，提交后由编辑部审核发布">
      <template #actions>
        <el-button @click="router.push('/media/content')">返回列表</el-button>
      </template>
    </PageHeader>

    <div class="publish-grid">
      <div class="main-col">
        <div class="card editor-card">
          <input
            v-model="form.title"
            class="title-input"
            maxlength="30"
            placeholder="请在这里输入标题"
          />
          <div class="title-meta">{{ form.title.length }} / 30</div>

          <div class="editor-wrap">
            <Toolbar class="toolbar" :editor="editorRef" :default-config="toolbarConfig" mode="default" />
            <Editor
              v-model="form.content"
              class="editor"
              :default-config="editorConfig"
              mode="default"
              @on-created="handleCreated"
            />
          </div>
        </div>
      </div>

      <aside class="side-col">
        <div class="card side-card">
          <h3>发布设置</h3>

          <div class="field">
            <label>频道 <em>*</em></label>
            <el-select v-model="form.channelId" placeholder="请选择频道" style="width: 100%">
              <el-option v-for="c in channels" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </div>

          <div class="field">
            <label>标签 <small>最多 5 个</small></label>
            <div class="labels">
              <el-tag
                v-for="(tag, index) in form.labels"
                :key="tag"
                closable
                effect="light"
                @close="form.labels.splice(index, 1)"
              >
                {{ tag }}
              </el-tag>
              <el-input
                v-if="form.labels.length < 5"
                v-model="labelInput"
                class="label-input"
                size="small"
                placeholder="输入后回车"
                @keyup.enter="addLabel"
              />
            </div>
          </div>

          <div class="field">
            <label>封面</label>
            <div class="cover-types">
              <button
                v-for="type in coverTypes"
                :key="type.value"
                type="button"
                class="cover-type"
                :class="{ active: form.coverType === type.value }"
                @click="changeCoverType(type.value)"
              >
                <el-icon><component :is="type.icon" /></el-icon>
                <span>{{ type.label }}</span>
              </button>
            </div>

            <div v-if="form.coverType === 0" class="cover-empty">
              无封面时，列表将以纯文字形式展示
            </div>

            <div v-else-if="form.coverType === -1" class="cover-empty">
              提交时自动提取正文中的第一张图片作为封面
            </div>

            <div v-else class="cover-area">
              <div class="cover-grid">
                <div v-for="(image, index) in form.coverImages" :key="image + index" class="cover-thumb">
                  <img :src="image" alt="封面" />
                  <button type="button" class="remove" @click="removeCover(index)">×</button>
                </div>
                <button
                  v-if="form.coverImages.length < coverLimit"
                  type="button"
                  class="add-cover"
                  @click="openPicker"
                >
                  <el-icon><Plus /></el-icon>
                  <span>选择图片</span>
                </button>
              </div>
              <p class="hint">
                建议尺寸 800×450；{{ form.coverType === 3 ? '三图封面需选择 3 张' : '单图封面选择 1 张' }}
              </p>
            </div>
          </div>
        </div>

        <div class="card tips-card">
          <h4>发布小贴士</h4>
          <ul>
            <li>标题控制在 30 字以内，突出时间、地点与事件。</li>
            <li>正文建议包含导语、现场细节和一句总结。</li>
            <li>提交后由审核员在审核工作台处理。</li>
          </ul>
        </div>
      </aside>
    </div>

    <div class="action-bar">
      <div class="bar-inner">
        <span class="status-tip">
          <el-icon><Document /></el-icon>
          {{ form.id ? '正在编辑草稿 #' + form.id : '新文章' }}
        </span>
        <div class="bar-actions">
          <el-button size="large" :loading="saving" @click="save(false)">存草稿</el-button>
          <el-button type="primary" size="large" :loading="submitting" @click="save(true)">
            提交审核
          </el-button>
        </div>
      </div>
    </div>

    <ImagePickerDialog
      v-model="pickerVisible"
      :limit="coverLimit"
      :selected="form.coverImages"
      @confirm="onPick"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import PageHeader from '@/components/PageHeader.vue'
import ImagePickerDialog from '@/components/ImagePickerDialog.vue'
import { createNews, getMediaNewsDetail, updateNews } from '@/api/media'
import { getChannels } from '@/api/news'

const route = useRoute()
const router = useRouter()

const channels = ref([])
const labelInput = ref('')
const pickerVisible = ref(false)
const saving = ref(false)
const submitting = ref(false)
const editorRef = shallowRef()

const form = reactive({
  id: null,
  title: '',
  content: '',
  channelId: null,
  labels: [],
  coverType: 1,
  coverImages: []
})

const coverTypes = [
  { value: 1, label: '单图', icon: 'Picture' },
  { value: 3, label: '三图', icon: 'Grid' },
  { value: 0, label: '无图', icon: 'DocumentRemove' },
  { value: -1, label: '自动', icon: 'MagicStick' }
]

const coverLimit = computed(() => (form.coverType === 3 ? 3 : 1))

const toolbarConfig = {
  excludeKeys: ['group-video', 'fullScreen']
}

const editorConfig = {
  placeholder: '请输入正文，支持插入图片、标题、引用……',
  MENU_CONF: {
    uploadImage: {
      server: '/api/media/materials',
      fieldName: 'file',
      maxFileSize: 10 * 1024 * 1024,
      allowedFileTypes: ['image/*'],
      headers: {
        Authorization: 'Bearer ' + (localStorage.getItem('campus_media_token') || '')
      },
      customInsert(res, insertFn) {
        if (res && res.code === 0 && res.data) {
          insertFn(res.data.url, '图片', res.data.url)
        } else {
          ElMessage.error((res && res.message) || '图片上传失败')
        }
      }
    }
  }
}

function handleCreated(editor) {
  editorRef.value = editor
}

function addLabel() {
  const value = labelInput.value.trim()
  if (!value) return
  if (form.labels.includes(value)) {
    ElMessage.warning('标签已存在')
    return
  }
  form.labels.push(value)
  labelInput.value = ''
}

function changeCoverType(value) {
  form.coverType = value
  if (value === 0 || value === -1) {
    form.coverImages = []
  } else if (value === 1) {
    form.coverImages = form.coverImages.slice(0, 1)
  }
}

function openPicker() {
  if (form.coverType === 0 || form.coverType === -1) {
    form.coverType = 1
  }
  pickerVisible.value = true
}

function onPick(images) {
  form.coverImages = images
}

function removeCover(index) {
  form.coverImages.splice(index, 1)
}

function htmlText(html) {
  return (html || '').replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim()
}

function resolveCover() {
  if (form.coverType !== -1) return
  const match = /<img[^>]+src="([^"]+)"/i.exec(form.content || '')
  if (match) {
    form.coverType = 1
    form.coverImages = [match[1]]
  } else {
    form.coverType = 0
    form.coverImages = []
  }
}

async function save(submit) {
  if (!form.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!htmlText(form.content)) {
    ElMessage.warning('请输入正文')
    return
  }
  if (!form.channelId) {
    ElMessage.warning('请选择频道')
    return
  }
  resolveCover()
  if (form.coverType > 0 && form.coverImages.length !== coverLimit.value) {
    ElMessage.warning('请选择 ' + coverLimit.value + ' 张封面图片')
    return
  }

  const payload = {
    title: form.title.trim(),
    content: form.content,
    channelId: form.channelId,
    labels: form.labels,
    coverType: form.coverType,
    coverImages: form.coverImages,
    submit
  }

  if (submit) submitting.value = true
  else saving.value = true
  try {
    if (form.id) {
      await updateNews(form.id, payload)
    } else {
      await createNews(payload)
    }
    ElMessage.success(submit ? '已提交审核，请等待审核员处理' : '草稿已保存')
    router.push('/media/content')
  } finally {
    saving.value = false
    submitting.value = false
  }
}

async function loadArticle() {
  const id = route.query.id
  if (!id) return
  const data = await getMediaNewsDetail(id)
  form.id = data.id
  form.title = data.title
  form.content = data.content
  form.channelId = data.channelId
  form.labels = data.labels ? data.labels.split(',').filter(Boolean) : []
  form.coverType = data.coverType ?? 0
  form.coverImages = data.coverList || []
}

onMounted(async () => {
  channels.value = await getChannels()
  await loadArticle()
})

onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor) editor.destroy()
})
</script>

<style scoped>
.publish-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 20px;
  align-items: start;
}

.editor-card {
  padding: 26px 30px 30px;
}

.title-input {
  width: 100%;
  border: 0;
  outline: 0;
  font-size: 26px;
  font-weight: 600;
  color: var(--text);
  padding: 4px 0 10px;
}

.title-input::placeholder {
  color: #c2c9d6;
}

.title-meta {
  text-align: right;
  color: var(--text-3);
  font-size: 12px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 18px;
}

.editor-wrap {
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
}

.editor-wrap :deep(.w-e-toolbar) {
  border-bottom: 1px solid var(--line);
  background: #fafbfe;
}

.editor-wrap :deep(.w-e-text-container) {
  height: 400px !important;
  overflow-y: auto;
}

.side-card {
  padding: 22px;
  position: sticky;
  top: 106px;
}

.side-card h3 {
  margin: 0 0 18px;
  font-size: 15px;
}

.field {
  margin-bottom: 20px;
}

.field > label {
  display: block;
  font-size: 13px;
  color: var(--text-2);
  margin-bottom: 8px;
}

.field > label em {
  color: var(--danger);
  font-style: normal;
}

.field > label small {
  color: var(--text-3);
  margin-left: 6px;
}

.labels {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}

.label-input {
  width: 110px;
}

.cover-types {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.cover-type {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 9px;
  padding: 9px 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-2);
  cursor: pointer;
  transition: all 0.18s;
}

.cover-type .el-icon {
  font-size: 17px;
}

.cover-type:hover {
  border-color: #b9cdf7;
}

.cover-type.active {
  border-color: var(--brand);
  color: var(--brand);
  background: var(--brand-soft);
  font-weight: 600;
}

.cover-empty {
  margin-top: 12px;
  padding: 14px;
  border-radius: 9px;
  background: #f7f9fc;
  color: var(--text-3);
  font-size: 12px;
  text-align: center;
}

.cover-area {
  margin-top: 12px;
}

.cover-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.cover-thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  border-radius: 8px;
  overflow: hidden;
}

.cover-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-thumb .remove {
  position: absolute;
  top: 3px;
  right: 3px;
  width: 20px;
  height: 20px;
  border: 0;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.7);
  color: #fff;
  cursor: pointer;
  line-height: 1;
}

.add-cover {
  aspect-ratio: 16 / 9;
  border: 1px dashed #c9d5ea;
  border-radius: 8px;
  background: #f8faff;
  color: var(--text-3);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  font-size: 11px;
  cursor: pointer;
}

.add-cover:hover {
  border-color: var(--brand);
  color: var(--brand);
  background: var(--brand-soft);
}

.hint {
  margin: 8px 0 0;
  font-size: 11px;
  color: var(--text-3);
}

.tips-card {
  margin-top: 16px;
  padding: 20px 22px;
  background: linear-gradient(160deg, #fff, #f4f8ff);
}

.tips-card h4 {
  margin: 0 0 10px;
  font-size: 13px;
}

.tips-card ul {
  margin: 0;
  padding-left: 16px;
  color: var(--text-2);
  font-size: 12px;
  line-height: 1.9;
}

.action-bar {
  position: sticky;
  bottom: 0;
  margin-top: 22px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(10px);
  border-top: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: 0 -6px 24px rgba(31, 36, 48, 0.05);
}

.bar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
}

.status-tip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-3);
  font-size: 12px;
}

.bar-actions {
  display: flex;
  gap: 10px;
}

.bar-actions .el-button {
  min-width: 116px;
  border-radius: 10px;
}

@media (max-width: 1100px) {
  .publish-grid {
    grid-template-columns: 1fr;
  }
  .side-card {
    position: static;
  }
}

@media (max-width: 768px) {
  .editor-card {
    padding: 18px;
  }
  .title-input {
    font-size: 20px;
  }
  .editor-wrap :deep(.w-e-text-container) {
    height: 300px !important;
  }
}
</style>
