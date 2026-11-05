<template>
  <router-link :to="'/article/' + article.id" class="article-card" :class="{ 'no-cover': covers.length === 0 }">
    <div class="body">
      <div class="badges">
        <span v-if="article.isTop === 1" class="badge top">置顶</span>
        <span v-if="article.channelName" class="badge channel">{{ article.channelName }}</span>
      </div>
      <h3 class="title clamp-2">{{ article.title }}</h3>
      <p class="summary clamp-2">{{ summary }}</p>
      <div class="meta">
        <span class="author">{{ article.authorName }}</span>
        <span class="dot">·</span>
        <span>{{ time }}</span>
        <span class="dot">·</span>
        <span>{{ article.views }} 阅读</span>
      </div>
    </div>

    <div v-if="covers.length === 1" class="cover single">
      <img :src="covers[0]" :alt="article.title" loading="lazy" />
    </div>
    <div v-else-if="covers.length >= 3" class="cover triple">
      <img v-for="(cover, index) in covers.slice(0, 3)" :key="index" :src="cover" :alt="article.title" loading="lazy" />
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  article: { type: Object, required: true }
})

const covers = computed(() => props.article.coverList || [])
const time = computed(() =>
  props.article.publishTime ? dayjs(props.article.publishTime).format('MM-DD HH:mm') : '未发布'
)
const summary = computed(() => {
  const html = props.article.content || ''
  const text = html.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim()
  return text.length > 88 ? text.slice(0, 88) + '…' : text
})
</script>

<style scoped>
.article-card {
  display: flex;
  max-width: 100%;
  gap: 22px;
  padding: 22px 24px;
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  transition: transform 0.2s, box-shadow 0.2s;
  margin-bottom: 14px;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.badges {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  min-height: 20px;
}

.badge {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 5px;
  line-height: 18px;
}

.badge.top {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}

.badge.channel {
  background: var(--brand-soft);
  color: var(--brand);
}

.title {
  margin: 0 0 8px;
  font-size: 18px;
  line-height: 1.5;
  font-weight: 600;
  color: var(--text);
}

.summary {
  margin: 0 0 14px;
  color: var(--text-2);
  font-size: 13px;
  line-height: 1.7;
}

.meta {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--text-3);
  font-size: 12px;
}

.author {
  color: var(--text-2);
  font-weight: 500;
}

.dot {
  opacity: 0.6;
}

.cover {
  flex-shrink: 0;
}

.cover.single img {
  width: 208px;
  height: 132px;
  object-fit: cover;
  border-radius: 10px;
}

.cover.triple {
  display: grid;
  grid-template-columns: repeat(3, 92px);
  gap: 6px;
  align-content: center;
}

.cover.triple img {
  width: 92px;
  height: 92px;
  object-fit: cover;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .article-card {
    flex-direction: column-reverse;
    padding: 16px;
    gap: 12px;
  }
  .cover.single img {
    width: 100%;
    height: 180px;
  }
  .cover.triple {
    grid-template-columns: repeat(3, 1fr);
    width: 100%;
  }
  .cover.triple img {
    width: 100%;
    height: 100px;
  }
  .title {
    font-size: 16px;
  }
}
</style>
