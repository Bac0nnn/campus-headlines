<template>
  <div class="discover page">
    <div class="hero card">
      <div>
        <p class="eyebrow">DISCOVER CAMPUS</p>
        <h1>发现你的校园频道</h1>
        <p class="sub">从学院动态到社团活动，从讲座信息到失物招领，总有一个频道与你有关。</p>
      </div>
      <div class="hero-stats">
        <div><strong>{{ channels.length }}</strong><span>个频道</span></div>
        <div><strong>24</strong><span>篇内容</span></div>
        <div><strong>12</strong><span>位作者</span></div>
      </div>
    </div>

    <div class="grid">
      <button v-for="(channel, index) in channels" :key="channel.id" class="channel-card" @click="open(channel)">
        <span class="icon" :style="{ background: palettes[index % palettes.length] }">
          <el-icon><component :is="icons[index % icons.length]" /></el-icon>
        </span>
        <h3>{{ channel.name }}</h3>
        <p>{{ channel.description }}</p>
        <span class="go">
          进入频道
          <em>{{ stats[channel.id] || 0 }} 篇内容 →</em>
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getChannels, getChannelStats } from '@/api/news'

const router = useRouter()
const channels = ref([])
const stats = reactive({})

const icons = ['School', 'Reading', 'UserFilled', 'Trophy', 'Mic', 'Briefcase', 'Search']
const palettes = [
  'linear-gradient(135deg,#2f6bff,#7c3aed)',
  'linear-gradient(135deg,#0ea5e9,#22c55e)',
  'linear-gradient(135deg,#f59e0b,#ef4444)',
  'linear-gradient(135deg,#8b5cf6,#ec4899)',
  'linear-gradient(135deg,#0f766e,#22d3ee)',
  'linear-gradient(135deg,#166534,#84cc16)',
  'linear-gradient(135deg,#be123c,#f97316)'
]

function open(channel) {
  router.push({ path: '/', query: { channel: channel.id } })
}

onMounted(async () => {
  const [channelList, statList] = await Promise.all([getChannels(), getChannelStats()])
  channels.value = channelList
  ;(statList || []).forEach((item) => {
    stats[item.id] = item.total
  })
})
</script>

<style scoped>
.discover {
  padding-top: 24px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
  padding: 36px 40px;
  background: linear-gradient(135deg, #172554, #2f6bff 85%, #7c3aed 130%);
  color: #fff;
  margin-bottom: 22px;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 11px;
  letter-spacing: 3px;
  opacity: 0.6;
}

.hero h1 {
  margin: 0 0 10px;
  font-size: 28px;
}

.hero .sub {
  margin: 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 14px;
  max-width: 560px;
}

.hero-stats {
  display: flex;
  gap: 34px;
  flex-shrink: 0;
}

.hero-stats div {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-stats strong {
  font-size: 26px;
}

.hero-stats span {
  font-size: 12px;
  opacity: 0.65;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.channel-card {
  text-align: left;
  border: 0;
  background: #fff;
  border-radius: var(--radius);
  padding: 22px;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.channel-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
}

.icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 20px;
  margin-bottom: 4px;
}

.channel-card h3 {
  margin: 0;
  font-size: 16px;
}

.channel-card p {
  margin: 0;
  color: var(--text-3);
  font-size: 12px;
  line-height: 1.6;
  flex: 1;
}

.go {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: var(--brand);
}

.go em {
  font-style: normal;
  color: var(--text-3);
  font-size: 11px;
}

@media (max-width: 800px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 24px;
  }
  .hero h1 {
    font-size: 22px;
  }
  .hero-stats {
    gap: 22px;
  }
}
</style>
