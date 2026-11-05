<template>
  <div class="material-page">
    <PageHeader title="素材管理" subtitle="上传、收藏并复用你的校园图片素材">
      <template #actions>
        <el-upload :show-file-list="false" accept="image/*" :http-request="handleUpload">
          <el-button type="primary" :loading="uploading">
            <el-icon><Upload /></el-icon>
            上传图片
          </el-button>
        </el-upload>
      </template>
    </PageHeader>

    <div class="material-card">
      <div class="toolbar">
        <div class="tabs">
          <button :class="{ active: tab === 'all' }" @click="switchTab('all')">全部</button>
          <button :class="{ active: tab === 'collected' }" @click="switchTab('collected')">
            收藏
            <span v-if="collectedCount" class="count">{{ collectedCount }}</span>
          </button>
        </div>
        <div class="summary">已上传 <strong>{{ total }}</strong> 张图片</div>
      </div>

      <div v-loading="loading" class="grid-wrap">
        <div class="grid">
          <button class="upload-tile" @click="triggerUpload">
            <el-icon><Plus /></el-icon>
            <span>上传图片</span>
            <small>JPG / PNG / WEBP ≤ 10MB</small>
          </button>

          <div v-for="item in list" :key="item.id" class="material-item">
            <div class="thumb">
              <img :src="item.url" alt="素材" loading="lazy" />
              <div class="overlay">
                <button class="action" :class="{ active: item.isCollected === 1 }" @click="toggleCollect(item)">
                  <el-icon><StarFilled v-if="item.isCollected === 1" /><Star v-else /></el-icon>
                  {{ item.isCollected === 1 ? '已收藏' : '收藏' }}
                </button>
                <button class="action danger" @click="remove(item)">
                  <el-icon><Delete /></el-icon>
                  删除
                </button>
              </div>
            </div>
            <div class="meta">
              <span>{{ item.width }} × {{ item.height }}</span>
              <span>{{ formatTime(item.createTime) }}</span>
            </div>
          </div>
        </div>

        <EmptyState v-if="!loading && list.length === 0" title="暂无素材" description="点击上方按钮上传第一张图片" />
      </div>

      <div v-if="total > size" class="pager">
        <el-pagination
          v-model:current-page="page"
          background
          layout="prev, pager, next"
          :page-size="size"
          :total="total"
          @current-change="load"
        />
      </div>
    </div>

    <input ref="fileInput" type="file" accept="image/*" hidden @change="onFileChange" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import PageHeader from '@/components/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { collectMaterial, deleteMaterial, getMaterials, uploadMaterial } from '@/api/media'

const tab = ref('all')
const list = ref([])
const total = ref(0)
const page = ref(1)
const size = 20
const loading = ref(false)
const uploading = ref(false)
const collectedCount = ref(0)
const fileInput = ref()

async function load() {
  loading.value = true
  try {
    const data = await getMaterials({
      page: page.value,
      size,
      collected: tab.value === 'collected' ? true : undefined
    })
    list.value = data.records || []
    total.value = data.total || 0
    if (tab.value === 'all') {
      collectedCount.value = list.value.filter((item) => item.isCollected === 1).length
    }
  } finally {
    loading.value = false
  }
}

function switchTab(value) {
  tab.value = value
  page.value = 1
  load()
}

function triggerUpload() {
  fileInput.value?.click()
}

async function onFileChange(event) {
  const file = event.target.files?.[0]
  if (file) {
    await doUpload(file)
  }
  event.target.value = ''
}

async function handleUpload(options) {
  await doUpload(options.file)
}

async function doUpload(file) {
  uploading.value = true
  try {
    await uploadMaterial(file)
    ElMessage.success('上传成功')
    page.value = 1
    await load()
  } finally {
    uploading.value = false
  }
}

async function toggleCollect(item) {
  const data = await collectMaterial(item.id)
  item.isCollected = data.isCollected
  ElMessage.success(data.isCollected === 1 ? '已收藏' : '已取消收藏')
}

async function remove(item) {
  await ElMessageBox.confirm('删除后不可恢复，确定删除这张图片吗？', '删除素材', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  await deleteMaterial(item.id)
  ElMessage.success('已删除')
  load()
}

function formatTime(time) {
  return time ? dayjs(time).format('MM-DD HH:mm') : ''
}

onMounted(load)
</script>

<style scoped>
.material-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 20px 24px 24px;
  box-shadow: var(--shadow);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 20px;
}

.tabs {
  display: flex;
  gap: 6px;
  background: #f2f4f8;
  padding: 4px;
  border-radius: 10px;
}

.tabs button {
  border: 0;
  background: transparent;
  padding: 7px 18px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-2);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tabs button.active {
  background: #fff;
  color: var(--text);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(31, 36, 48, 0.08);
}

.count {
  background: var(--brand);
  color: #fff;
  font-size: 10px;
  border-radius: 999px;
  padding: 0 5px;
  line-height: 14px;
}

.summary {
  font-size: 13px;
  color: var(--text-3);
}

.summary strong {
  color: var(--brand);
  margin: 0 2px;
}

.grid-wrap {
  min-height: 220px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 18px;
}

.upload-tile {
  border: 1.5px dashed #c9d5ea;
  background: #f8faff;
  border-radius: 12px;
  min-height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--text-2);
  cursor: pointer;
  transition: all 0.2s;
}

.upload-tile:hover {
  border-color: var(--brand);
  color: var(--brand);
  background: var(--brand-soft);
}

.upload-tile .el-icon {
  font-size: 24px;
}

.upload-tile small {
  color: var(--text-3);
  font-size: 11px;
}

.material-item .thumb {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  background: #f2f4f8;
}

.material-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.material-item:hover img {
  transform: scale(1.04);
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0) 35%, rgba(15, 23, 42, 0.72));
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}

.material-item:hover .overlay {
  opacity: 1;
}

.action {
  border: 0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--text);
  font-size: 12px;
  padding: 5px 10px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.action.active {
  color: #d97706;
}

.action.danger:hover {
  background: #ef4444;
  color: #fff;
}

.meta {
  display: flex;
  justify-content: space-between;
  padding: 8px 2px 0;
  font-size: 11px;
  color: var(--text-3);
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 26px;
}
</style>
