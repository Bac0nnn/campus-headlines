<template>
  <div class="home page">
    <section v-if="hero && page === 1" class="hero">
      <router-link :to="'/article/' + hero.id" class="hero-card">
        <div class="hero-content">
          <div class="hero-badges">
            <span class="pill">头条</span>
            <span class="pill ghost">{{ hero.channelName }}</span>
          </div>
          <h1>{{ hero.title }}</h1>
          <p class="hero-summary">{{ heroSummary }}</p>
          <div class="hero-meta">
            <img :src="hero.authorAvatar" alt="author" />
            <span>{{ hero.authorName }}</span>
            <span class="dot">·</span>
            <span>{{ formatTime(hero.publishTime) }}</span>
            <span class="dot">·</span>
            <span>{{ hero.views }} 阅读</span>
          </div>
        </div>
        <div class="hero-visual">
          <img v-if="heroCoverUrl" :src="heroCoverUrl" :alt="hero.title" />
        </div>
      </router-link>
    </section>

    <div class="layout">
      <main class="feed">
        <div class="feed-head">
          <ChannelNav v-model="channelId" :channels="channels" @update:model-value="onChannelChange" />
          <div class="tip">
            <el-icon><Bell /></el-icon>
            在「{{ currentChannelName }}」频道为您更新了新闻
          </div>
        </div>

        <div v-loading="loading" class="list">
          <ArticleCard v-for="item in feed" :key="item.id" :article="item" />

          <EmptyState
            v-if="!loading && feed.length === 0"
            :title="keyword ? '没有找到相关新闻' : '该频道暂时没有内容'"
            :description="keyword ? '换个关键词试试，或回到推荐频道' : '内容正在赶来的路上'"
          >
            <el-button v-if="keyword" @click="clearSearch">清除搜索</el-button>
          </EmptyState>

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
      </main>

      <aside class="sidebar">
        <div class="panel">
          <div class="panel-head">
            <h3>热读榜</h3>
            <span>实时更新</span>
          </div>
          <ol class="hot-list">
            <li v-for="(item, index) in hot" :key="item.id">
              <router-link :to="'/article/' + item.id">
                <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
                <span class="hot-title clamp-2">{{ item.title }}</span>
              </router-link>
            </li>
          </ol>
        </div>

        <div class="panel">
          <div class="panel-head">
            <h3>校园服务</h3>
          </div>
          <div class="service-grid">
            <button v-for="item in services" :key="item.name" class="service" @click="goChannel(item.channel)">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.name }}</span>
            </button>
          </div>
        </div>

        <div class="panel brand-panel">
          <p class="brand-tip">有新闻线索？</p>
          <h3>欢迎向校媒中心投稿</h3>
          <p class="brand-desc">文字、图片、短视频均可，审核通过后将出现在校园头条。</p>
          <el-button round class="cta" @click="goMedia">进入创作中心</el-button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import ChannelNav from '@/components/ChannelNav.vue'
import ArticleCard from '@/components/ArticleCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getChannels, getNewsList } from '@/api/news'

const route = useRoute()
const router = useRouter()

const channels = ref([])
const list = ref([])
const hot = ref([])
const total = ref(0)
const page = ref(1)
const size = 8
const loading = ref(false)
const channelId = ref(route.query.channel ? Number(route.query.channel) : null)
const keyword = ref((route.query.keyword || '').toString())

const services = [
  { name: '讲座', channel: 5, icon: 'Reading' },
  { name: '失物', channel: 7, icon: 'Search' },
  { name: '就业', channel: 6, icon: 'Briefcase' },
  { name: '社团', channel: 3, icon: 'UserFilled' }
]

const hero = computed(() => (page.value === 1 && list.value.length ? list.value[0] : null))
const feed = computed(() => (hero.value ? list.value.slice(1) : list.value))
const currentChannelName = computed(() => {
  if (!channelId.value) return '推荐'
  const found = channels.value.find((item) => item.id === channelId.value)
  return found ? found.name : '推荐'
})
const heroCoverUrl = computed(() => hero.value?.coverList?.[0] || '')
const heroSummary = computed(() => {
  const text = (hero.value?.content || '').replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim()
  return text.length > 96 ? text.slice(0, 96) + '…' : text
})

function formatTime(time) {
  return time ? dayjs(time).format('MM-DD HH:mm') : ''
}

async function load() {
  loading.value = true
  try {
    const data = await getNewsList({
      page: page.value,
      size,
      channelId: channelId.value || undefined,
      keyword: keyword.value || undefined
    })
    list.value = data.records || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function loadHot() {
  const data = await getNewsList({ page: 1, size: 5 })
  hot.value = data.records || []
}

function onChannelChange(id) {
  channelId.value = id
  page.value = 1
  const query = {}
  if (id) query.channel = id
  if (keyword.value) query.keyword = keyword.value
  router.replace({ path: '/', query })
  load()
}

function goChannel(id) {
  onChannelChange(id)
}

function goMedia() {
  window.open('/media/login', '_blank')
}

function clearSearch() {
  keyword.value = ''
  router.replace({ path: '/', query: channelId.value ? { channel: channelId.value } : {} })
  page.value = 1
  load()
}

watch(
  () => route.query,
  (query) => {
    const nextChannel = query.channel ? Number(query.channel) : null
    const nextKeyword = (query.keyword || '').toString()
    if (nextChannel !== channelId.value || nextKeyword !== keyword.value) {
      channelId.value = nextChannel
      keyword.value = nextKeyword
      page.value = 1
      load()
    }
  }
)

onMounted(async () => {
  channels.value = await getChannels()
  await Promise.all([load(), loadHot()])
})
</script>

<style scoped>
.home {
  padding-top: 24px;
}

.hero {
  margin-bottom: 26px;
}

.hero-card {
  display: block;
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
  height: 340px;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, #0d1730 0%, #16295a 60%, #1b3a7a 100%);
  box-shadow: 0 20px 50px rgba(23, 35, 75, 0.18);
}

.hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px 44px;
  color: #fff;
}

.hero-visual {
  position: relative;
  overflow: hidden;
}

.hero-visual img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.02);
  transition: transform 0.7s ease;
}

.hero-card:hover .hero-visual img {
  transform: scale(1.07);
}

.hero-visual::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, #16295a 0%, rgba(22, 41, 90, 0.55) 20%, rgba(22, 41, 90, 0) 52%);
}

.hero-badges {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.pill {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--accent);
  font-weight: 600;
}

.pill.ghost {
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(6px);
  font-weight: 400;
}

.hero-content h1 {
  margin: 0 0 10px;
  font-size: 30px;
  line-height: 1.42;
  letter-spacing: 0.4px;
}

.hero-summary {
  margin: 0 0 16px;
  color: rgba(255, 255, 255, 0.78);
  font-size: 14px;
  line-height: 1.7;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.72);
}

.hero-meta img {
  width: 26px;
  height: 26px;
  border-radius: 50%;
}

.dot {
  opacity: 0.6;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 316px;
  gap: 24px;
  align-items: start;
}

.feed-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: #fff;
  border-radius: var(--radius);
  padding: 10px 18px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.feed-head :deep(.channel-nav) {
  padding: 0;
  flex: 1;
  min-width: 0;
}

.tip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--text-3);
  font-size: 12px;
}

.feed {
  min-width: 0;
}

.list {
  min-height: 300px;
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 22px;
}

.sidebar {
  position: sticky;
  top: 88px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel {
  background: #fff;
  border-radius: var(--radius);
  padding: 18px 20px;
  box-shadow: var(--shadow);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.panel-head h3 {
  margin: 0;
  font-size: 15px;
  position: relative;
  padding-left: 10px;
}

.panel-head h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 3px;
  bottom: 3px;
  width: 3px;
  border-radius: 3px;
  background: var(--brand);
}

.panel-head span {
  font-size: 11px;
  color: var(--text-3);
}

.hot-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.hot-list li + li {
  margin-top: 12px;
}

.hot-list a {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.rank {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  display: grid;
  place-items: center;
  font-size: 11px;
  font-weight: 700;
  background: #f2f4f8;
  color: var(--text-3);
  flex-shrink: 0;
  margin-top: 2px;
}

.rank-1 {
  background: #ffeceb;
  color: #ef4444;
}
.rank-2 {
  background: #fff4e5;
  color: #f97316;
}
.rank-3 {
  background: #fff9db;
  color: #eab308;
}

.hot-title {
  font-size: 13px;
  line-height: 1.55;
  color: var(--text);
}

.hot-list a:hover .hot-title {
  color: var(--brand);
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.service {
  border: 1px solid var(--line);
  background: #fbfcff;
  border-radius: 10px;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-2);
  cursor: pointer;
  transition: all 0.18s;
}

.service .el-icon {
  font-size: 19px;
  color: var(--brand);
}

.service:hover {
  border-color: #bfd2ff;
  background: var(--brand-soft);
  color: var(--brand);
  transform: translateY(-1px);
}

.brand-panel {
  background: linear-gradient(150deg, #172554, #2f6bff 120%);
  color: #fff;
}

.brand-panel .brand-tip {
  margin: 0;
  font-size: 11px;
  opacity: 0.6;
  letter-spacing: 1px;
}

.brand-panel h3 {
  margin: 6px 0 8px;
  font-size: 17px;
}

.brand-desc {
  margin: 0 0 14px;
  font-size: 12px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.7);
}

.cta {
  background: #fff;
  color: var(--brand-dark);
  border: 0;
  font-weight: 600;
}

@media (max-width: 1080px) {
  .layout {
    grid-template-columns: minmax(0, 1fr);
  }
  .sidebar {
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
  }
  .sidebar .panel {
    flex: 1;
    min-width: 260px;
  }
}

@media (max-width: 768px) {
  .home {
    padding-top: 14px;
  }
  .hero-card {
    grid-template-columns: 1fr;
    height: auto;
    border-radius: 16px;
  }
  .hero-visual {
    display: none;
  }
  .hero-content {
    padding: 24px;
  }
  .hero-content h1 {
    font-size: 20px;
  }
  .hero-summary {
    display: none;
  }
  .feed-head {
    padding: 8px 12px;
    min-width: 0;
  }
  .tip {
    width: 100%;
    padding-bottom: 4px;
  }
  .sidebar {
    display: none;
  }
}
</style>
