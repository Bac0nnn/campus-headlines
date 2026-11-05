<template>
  <div class="audit-page">
    <PageHeader title="审核工作台" subtitle="审核校园媒体提交的稿件，通过后立即在用户端发布">
      <template #actions>
        <el-button :loading="loading" @click="reload">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </template>
    </PageHeader>

    <div class="stat-row">
      <div class="stat-card pending">
        <span class="label">待审核</span>
        <strong>{{ counts[1] }}</strong>
        <span class="hint">需要尽快处理</span>
      </div>
      <div class="stat-card passed">
        <span class="label">已通过</span>
        <strong>{{ counts[2] }}</strong>
        <span class="hint">已发布到用户端</span>
      </div>
      <div class="stat-card rejected">
        <span class="label">已驳回</span>
        <strong>{{ counts[3] }}</strong>
        <span class="hint">等待作者修改</span>
      </div>
      <div class="stat-card tip-card">
        <el-icon><InfoFilled /></el-icon>
        <p>驳回时必须填写审核意见，作者可在内容列表中看到状态并修改后重新提交。</p>
      </div>
    </div>

    <div class="card list-card">
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="tab"
          :class="{ active: status === tab.value }"
          @click="switchStatus(tab.value)"
        >
          {{ tab.label }}
          <span v-if="tab.value === 1 && counts[1]">{{ counts[1] }}</span>
        </button>
      </div>

      <div v-loading="loading" class="list">
        <div v-for="item in list" :key="item.id" class="audit-row">
          <div class="cover">
            <img v-if="coverOf(item)" :src="coverOf(item)" :alt="item.title" loading="lazy" />
            <div v-else class="no-cover"><el-icon><Picture /></el-icon></div>
          </div>

          <div class="info">
            <div class="title-line">
              <h3>{{ item.title }}</h3>
              <StatusTag :status="item.status" />
            </div>
            <p class="excerpt">{{ excerpt(item.content) }}</p>
            <div class="meta">
              <span>{{ item.authorName }}</span>
              <span class="dot">·</span>
              <span>{{ item.channelName }}</span>
              <span class="dot">·</span>
              <span>{{ formatTime(item.updateTime) }}</span>
            </div>
          </div>

          <div class="actions">
            <el-button text type="primary" @click="openDetail(item)">查看全文</el-button>
            <template v-if="item.status === 1">
              <el-button type="success" size="small" @click="approve(item)">通过</el-button>
              <el-button type="danger" plain size="small" @click="openReject(item)">驳回</el-button>
            </template>
          </div>
        </div>

        <EmptyState
          v-if="!loading && list.length === 0"
          :title="status === 1 ? '暂无待审核稿件' : '暂无相关记录'"
          description="新的稿件提交后会出现在这里"
        />

        <div v-if="total > size" class="pager">
          <el-pagination
            v-model:current-page="page"
            background
            layout="total, prev, pager, next"
            :page-size="size"
            :total="total"
            @current-change="load"
          />
        </div>
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="稿件详情" width="760px" top="5vh" append-to-body>
      <div v-if="current" class="detail">
        <div class="detail-badges">
          <StatusTag :status="current.status" />
          <span class="channel">{{ current.channelName }}</span>
        </div>
        <h2>{{ current.title }}</h2>
        <p class="detail-meta">
          {{ current.authorName }} · {{ formatTime(current.publishTime || current.updateTime) }}
        </p>
        <div class="detail-body" v-html="current.content"></div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <template v-if="current && current.status === 1">
          <el-button type="danger" plain @click="openReject(current)">驳回</el-button>
          <el-button type="success" @click="approve(current)">通过并发布</el-button>
        </template>
      </template>
    </el-dialog>

    <el-dialog v-model="rejectVisible" title="驳回稿件" width="480px" append-to-body>
      <p class="reject-tip">请填写驳回原因，作者会在内容列表中看到该意见。</p>
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="4"
        maxlength="200"
        show-word-limit
        placeholder="例如：标题与正文不符，请补充现场图片后重新提交"
      />
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" :loading="reviewing" @click="reject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getAuditNews, getAuditNewsDetail, reviewNews } from '@/api/media'

const tabs = [
  { label: '待审核', value: 1 },
  { label: '已通过', value: 2 },
  { label: '已驳回', value: 3 }
]

const status = ref(1)
const list = ref([])
const total = ref(0)
const page = ref(1)
const size = 6
const loading = ref(false)
const reviewing = ref(false)
const detailVisible = ref(false)
const rejectVisible = ref(false)
const current = ref(null)
const rejectReason = ref('')
const counts = reactive({ 1: 0, 2: 0, 3: 0 })

function coverOf(item) {
  return item.coverList && item.coverList.length ? item.coverList[0] : ''
}

function excerpt(html) {
  const text = (html || '').replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim()
  return text.length > 100 ? text.slice(0, 100) + '…' : text
}

function formatTime(time) {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '—'
}

async function load() {
  loading.value = true
  try {
    const data = await getAuditNews({ status: status.value, page: page.value, size })
    list.value = data.records || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function loadCounts() {
  const [pending, passed, rejected] = await Promise.all([
    getAuditNews({ status: 1, page: 1, size: 1 }),
    getAuditNews({ status: 2, page: 1, size: 1 }),
    getAuditNews({ status: 3, page: 1, size: 1 })
  ])
  counts[1] = pending.total || 0
  counts[2] = passed.total || 0
  counts[3] = rejected.total || 0
}

function reload() {
  load()
  loadCounts()
}

function switchStatus(value) {
  status.value = value
  page.value = 1
  load()
}

async function openDetail(item) {
  const data = await getAuditNewsDetail(item.id)
  current.value = data
  detailVisible.value = true
}

async function approve(item) {
  await ElMessageBox.confirm('通过后文章将立即在用户端发布，确定通过《' + item.title + '》吗？', '审核通过', {
    confirmButtonText: '通过并发布',
    cancelButtonText: '再看看',
    type: 'success'
  })
  reviewing.value = true
  try {
    await reviewNews(item.id, { pass: true, reason: '内容符合校园头条发布规范' })
    ElMessage.success('已通过并发布')
    detailVisible.value = false
    reload()
  } finally {
    reviewing.value = false
  }
}

function openReject(item) {
  current.value = item
  rejectReason.value = ''
  rejectVisible.value = true
}

async function reject() {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  reviewing.value = true
  try {
    await reviewNews(current.value.id, { pass: false, reason: rejectReason.value.trim() })
    ElMessage.success('已驳回，作者可修改后重新提交')
    rejectVisible.value = false
    detailVisible.value = false
    reload()
  } finally {
    reviewing.value = false
  }
}

onMounted(() => {
  reload()
})
</script>

<style scoped>
.stat-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr)) 1.4fr;
  gap: 14px;
  margin-bottom: 16px;
}

.stat-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 18px 20px;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-top: 3px solid transparent;
}

.stat-card .label { font-size: 12px; color: var(--text-3); }
.stat-card strong { font-size: 28px; line-height: 1.2; }
.stat-card .hint { font-size: 11px; color: var(--text-3); }

.stat-card.pending { border-top-color: #f59e0b; }
.stat-card.pending strong { color: #d97706; }
.stat-card.passed { border-top-color: #22c55e; }
.stat-card.passed strong { color: #16a34a; }
.stat-card.rejected { border-top-color: #ef4444; }
.stat-card.rejected strong { color: #dc2626; }

.tip-card {
  background: linear-gradient(135deg, #f7f9ff, #eef3ff);
  border-top-color: #2f6bff;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.tip-card .el-icon { color: var(--brand); font-size: 22px; flex-shrink: 0; }
.tip-card p { margin: 0; font-size: 12px; color: var(--text-2); line-height: 1.7; }

.list-card { padding: 18px 22px 22px; }

.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 10px;
}

.tab {
  border: 0;
  background: transparent;
  padding: 8px 16px 12px;
  color: var(--text-2);
  font-size: 14px;
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab span {
  background: #fff2d9;
  color: #d97706;
  border-radius: 999px;
  font-size: 11px;
  padding: 0 7px;
  line-height: 17px;
}

.tab.active { color: var(--brand); font-weight: 600; }
.tab.active::after {
  content: '';
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: -1px;
  height: 2px;
  background: var(--brand);
  border-radius: 2px;
}

.audit-row {
  display: flex;
  gap: 16px;
  padding: 16px 4px;
  border-bottom: 1px solid var(--line);
  align-items: flex-start;
}

.audit-row:last-child { border-bottom: 0; }

.cover {
  width: 150px;
  height: 88px;
  flex-shrink: 0;
  border-radius: 9px;
  overflow: hidden;
  background: #f2f4f8;
}

.cover img { width: 100%; height: 100%; object-fit: cover; }

.no-cover {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: #c3cbd9;
  font-size: 24px;
}

.info { flex: 1; min-width: 0; }

.title-line { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.title-line h3 { margin: 0; font-size: 16px; font-weight: 600; }

.excerpt {
  margin: 0 0 8px;
  color: var(--text-2);
  font-size: 12px;
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta { display: flex; gap: 6px; color: var(--text-3); font-size: 12px; }
.meta .dot { opacity: 0.6; }

.actions { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }

.pager { display: flex; justify-content: center; margin-top: 20px; }

.detail-badges { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.detail-badges .channel {
  font-size: 12px;
  color: var(--brand);
  background: var(--brand-soft);
  padding: 2px 9px;
  border-radius: 6px;
}

.detail h2 { margin: 0 0 8px; font-size: 22px; line-height: 1.5; }
.detail-meta { margin: 0 0 16px; color: var(--text-3); font-size: 12px; }

.detail-body {
  max-height: 52vh;
  overflow-y: auto;
  line-height: 1.9;
  font-size: 14px;
  color: var(--text-2);
  border-top: 1px solid var(--line);
  padding-top: 14px;
}

.detail-body :deep(img) { max-width: 100%; border-radius: 10px; }
.detail-body :deep(h3) { border-left: 3px solid var(--brand); padding-left: 10px; font-size: 16px; }
.detail-body :deep(blockquote) { background: #f7f9fd; padding: 10px 14px; border-radius: 8px; margin: 14px 0; }

.reject-tip { margin: 0 0 12px; font-size: 13px; color: var(--text-2); }

@media (max-width: 1100px) {
  .stat-row { grid-template-columns: repeat(2, 1fr); }
  .tip-card { grid-column: span 2; }
}

@media (max-width: 768px) {
  .stat-row { grid-template-columns: 1fr; }
  .tip-card { grid-column: auto; }
  .audit-row { flex-wrap: wrap; }
  .cover { width: 100%; height: 160px; }
  .actions { width: 100%; justify-content: flex-end; }
}
</style>
