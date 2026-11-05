<template>
  <div class="content-page">
    <PageHeader title="内容列表" subtitle="查看并管理你发布的全部文章">
      <template #actions>
        <el-button type="primary" @click="router.push('/media/publish')">
          <el-icon><Plus /></el-icon>
          写文章
        </el-button>
      </template>
    </PageHeader>

    <div class="card filter-card">
      <div class="status-tabs">
        <button
          v-for="tab in statusTabs"
          :key="String(tab.value)"
          class="status-tab"
          :class="{ active: filters.status === tab.value }"
          @click="setStatus(tab.value)"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="filters">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索标题关键词"
          clearable
          class="keyword"
          @keyup.enter="search"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filters.channelId" placeholder="全部频道" clearable class="channel">
          <el-option v-for="c in channels" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="daterange"
        />
        <el-button type="primary" @click="search">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>
    </div>

    <div v-loading="loading" class="list">
      <div v-for="item in list" :key="item.id" class="news-row">
        <div class="cover">
          <img v-if="coverOf(item)" :src="coverOf(item)" :alt="item.title" loading="lazy" />
          <div v-else class="no-cover"><el-icon><Picture /></el-icon></div>
        </div>

        <div class="info">
          <div class="title-line">
            <h3>{{ item.title }}</h3>
            <StatusTag :status="item.status" />
          </div>
          <div class="meta">
            <span>{{ item.channelName }}</span>
            <span class="dot">·</span>
            <span>{{ formatTime(item.publishTime || item.updateTime) }}</span>
            <span class="dot">·</span>
            <span>{{ item.views }} 阅读</span>
            <span class="dot">·</span>
            <span>{{ item.likes }} 点赞</span>
          </div>
          <div v-if="labelsOf(item).length" class="labels">
            <el-tag v-for="label in labelsOf(item)" :key="label" size="small" type="info" effect="plain">
              {{ label }}
            </el-tag>
          </div>
        </div>

        <div class="actions">
          <el-button text type="primary" :disabled="item.status === 2" @click="edit(item)">编辑</el-button>
          <el-button text type="danger" @click="remove(item)">删除</el-button>
        </div>
      </div>

      <EmptyState
        v-if="!loading && list.length === 0"
        title="这里还没有文章"
        description="换一个筛选条件，或去写一篇校园新闻"
      >
        <el-button type="primary" @click="router.push('/media/publish')">去写文章</el-button>
      </EmptyState>

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
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import { deleteNews, getMediaNews } from '@/api/media'
import { getChannels } from '@/api/news'

const router = useRouter()

const channels = ref([])
const list = ref([])
const total = ref(0)
const page = ref(1)
const size = 6
const loading = ref(false)

const statusTabs = [
  { label: '全部', value: null },
  { label: '草稿', value: 0 },
  { label: '待审核', value: 1 },
  { label: '审核通过', value: 2 },
  { label: '审核失败', value: 3 }
]

const filters = reactive({
  status: null,
  keyword: '',
  channelId: null,
  dateRange: []
})

function coverOf(item) {
  return item.coverList && item.coverList.length ? item.coverList[0] : ''
}

function labelsOf(item) {
  return item.labels ? item.labels.split(',').filter(Boolean) : []
}

function formatTime(time) {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '—'
}

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      size
    }
    if (filters.status !== null) params.status = filters.status
    if (filters.keyword.trim()) params.keyword = filters.keyword.trim()
    if (filters.channelId) params.channelId = filters.channelId
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.startDate = filters.dateRange[0]
      params.endDate = filters.dateRange[1]
    }
    const data = await getMediaNews(params)
    list.value = data.records || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

function setStatus(value) {
  filters.status = value
  page.value = 1
  load()
}

function search() {
  page.value = 1
  load()
}

function reset() {
  filters.status = null
  filters.keyword = ''
  filters.channelId = null
  filters.dateRange = []
  page.value = 1
  load()
}

function edit(item) {
  router.push({ path: '/media/publish', query: { id: item.id } })
}

async function remove(item) {
  await ElMessageBox.confirm('删除后不可恢复，确定删除《' + item.title + '》吗？', '删除文章', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  await deleteNews(item.id)
  ElMessage.success('已删除')
  if (list.value.length === 1 && page.value > 1) page.value -= 1
  load()
}

onMounted(async () => {
  channels.value = await getChannels()
  await load()
})
</script>

<style scoped>
.filter-card {
  padding: 18px 22px 20px;
  margin-bottom: 16px;
}

.status-tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 16px;
  overflow-x: auto;
}

.status-tab {
  border: 0;
  background: transparent;
  padding: 8px 16px 12px;
  font-size: 14px;
  color: var(--text-2);
  cursor: pointer;
  position: relative;
  white-space: nowrap;
}

.status-tab:hover {
  color: var(--brand);
}

.status-tab.active {
  color: var(--brand);
  font-weight: 600;
}

.status-tab.active::after {
  content: '';
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: -1px;
  height: 2px;
  background: var(--brand);
  border-radius: 2px;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.keyword {
  width: 230px;
}

.channel {
  width: 150px;
}

.daterange {
  width: 250px !important;
}

.list {
  min-height: 260px;
}

.news-row {
  display: flex;
  gap: 18px;
  background: #fff;
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 12px;
  box-shadow: var(--shadow);
  transition: box-shadow 0.2s, transform 0.2s;
}

.news-row:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-hover);
}

.cover {
  width: 168px;
  height: 96px;
  flex-shrink: 0;
  border-radius: 9px;
  overflow: hidden;
  background: #f2f4f8;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: #c3cbd9;
  font-size: 26px;
}

.info {
  flex: 1;
  min-width: 0;
}

.title-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.title-line h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-3);
  font-size: 12px;
  margin-bottom: 8px;
}

.meta .dot {
  opacity: 0.6;
}

.labels {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 22px;
}

@media (max-width: 768px) {
  .news-row {
    flex-wrap: wrap;
  }
  .cover {
    width: 100%;
    height: 160px;
  }
  .actions {
    width: 100%;
    justify-content: flex-end;
  }
  .keyword,
  .channel,
  .daterange {
    width: 100% !important;
  }
}
</style>
