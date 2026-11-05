<template>
  <div class="detail-page page">
    <div class="topbar">
      <router-link to="/" class="back">
        <el-icon><ArrowLeft /></el-icon>
        返回首页
      </router-link>
      <span class="crumb" v-if="article">{{ article.channelName }} / 正文</span>
    </div>

    <div v-if="loading" class="loading-card card" v-loading="true" style="height: 320px"></div>

    <div v-else-if="!article" class="notfound card">
      <EmptyState title="文章不存在或已下架" description="它可能已被作者删除，去看看其他校园新闻吧">
        <el-button type="primary" @click="$router.push('/')">回到首页</el-button>
      </EmptyState>
    </div>

    <template v-else>
      <div class="detail-layout">
        <article class="article card">
          <div class="article-head">
            <div class="badges">
              <span class="channel">{{ article.channelName }}</span>
              <span v-if="article.isTop === 1" class="top">置顶</span>
            </div>
            <h1>{{ article.title }}</h1>
            <div class="author-row">
              <img :src="article.authorAvatar" alt="author" />
              <div class="author-info">
                <strong>{{ article.authorName }}</strong>
                <span>{{ formatTime(article.publishTime) }} · {{ article.views }} 阅读</span>
              </div>
              <el-button
                class="follow"
                :type="following ? 'default' : 'primary'"
                round
                size="small"
                @click="toggleFollow"
              >
                {{ following ? '已关注' : '+ 关注' }}
              </el-button>
            </div>
          </div>

          <div v-if="article.coverList && article.coverList.length" class="detail-cover" :class="{ triple: article.coverList.length >= 3 }">
            <img v-for="(cover, index) in article.coverList" :key="index" :src="cover" :alt="article.title" />
          </div>

          <div class="article-body" v-html="article.content"></div>

          <div class="article-actions">
            <button class="action like" :class="{ active: article.liked }" @click="like">
              <el-icon><CaretTop /></el-icon>
              <span>{{ article.liked ? '已点赞' : '点赞' }}</span>
              <em>{{ article.likes }}</em>
            </button>
            <button class="action" @click="dislike">
              <el-icon><CaretBottom /></el-icon>
              不喜欢
            </button>
            <button class="action" @click="share">
              <el-icon><Share /></el-icon>
              分享
            </button>
            <span class="action-tip">内容由校园媒体发布，转载请注明来源</span>
          </div>
        </article>

        <aside class="aside">
          <div class="card author-card">
            <img :src="article.authorAvatar" alt="author" class="big-avatar" />
            <h3>{{ article.authorName }}</h3>
            <p>校园头条认证媒体号</p>
            <div class="author-stats">
              <div><strong>{{ related.length + 3 }}</strong><span>发布</span></div>
              <div><strong>{{ article.views }}</strong><span>阅读</span></div>
              <div><strong>{{ article.likes }}</strong><span>获赞</span></div>
            </div>
          </div>

          <div v-if="related.length" class="card related">
            <h3>相关推荐</h3>
            <router-link v-for="item in related" :key="item.id" :to="'/article/' + item.id" class="related-item">
              <span class="clamp-2">{{ item.title }}</span>
              <small>{{ item.views }} 阅读</small>
            </router-link>
          </div>
        </aside>
      </div>

      <section class="comments card">
        <div class="comments-head">
          <h3>评论 <span>{{ comments.length }}</span></h3>
          <span class="sort">按时间倒序</span>
        </div>

        <div class="comment-form">
          <img :src="user.isLogin ? user.avatar : '/avatars/u1.svg'" alt="me" />
          <div class="input-wrap">
            <el-input
              v-model="commentText"
              type="textarea"
              :rows="2"
              maxlength="200"
              show-word-limit
              placeholder="说点什么吧，你的评论会出现在这里…"
            />
            <div class="form-actions">
              <span class="login-hint" v-if="!user.isLogin">登录后即可参与评论</span>
              <el-button type="primary" :loading="posting" @click="postComment">发表评论</el-button>
            </div>
          </div>
        </div>

        <div class="comment-list">
          <div v-for="comment in comments" :key="comment.id" class="comment">
            <img :src="comment.avatar" alt="avatar" />
            <div class="comment-main">
              <div class="comment-head">
                <strong>{{ comment.nickname }}</strong>
                <span>{{ formatTime(comment.createTime) }}</span>
              </div>
              <p>{{ comment.content }}</p>
            </div>
          </div>
          <EmptyState v-if="comments.length === 0" title="还没有评论" description="来抢第一条评论吧" />
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import EmptyState from '@/components/EmptyState.vue'
import { addComment, getComments, getNewsDetail, getNewsList, toggleLike } from '@/api/news'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const user = useUserStore()

const article = ref(null)
const comments = ref([])
const related = ref([])
const loading = ref(true)
const posting = ref(false)
const commentText = ref('')
const following = ref(false)

function formatTime(time) {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : ''
}

function requireLogin() {
  if (user.isLogin) return true
  ElMessage.warning('请先登录')
  router.push({ path: '/login', query: { redirect: route.fullPath } })
  return false
}

async function load() {
  loading.value = true
  article.value = null
  try {
    const data = await getNewsDetail(route.params.id)
    article.value = data
    const [commentList, relatedList] = await Promise.all([
      getComments(data.id),
      getNewsList({ channelId: data.channelId, page: 1, size: 5 })
    ])
    comments.value = commentList || []
    related.value = (relatedList.records || []).filter((item) => item.id !== data.id).slice(0, 4)
  } catch (e) {
    article.value = null
  } finally {
    loading.value = false
  }
}

async function like() {
  if (!requireLogin()) return
  const result = await toggleLike(article.value.id)
  article.value.liked = result.liked
  article.value.likes = result.likes
}

function dislike() {
  ElMessage.success('已减少此类内容推荐')
}

async function share() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    ElMessage.success('链接已复制，快分享给同学吧')
  } catch (e) {
    ElMessage.info(window.location.href)
  }
}

function toggleFollow() {
  if (!requireLogin()) return
  following.value = !following.value
  ElMessage.success(following.value ? '已关注该媒体号' : '已取消关注')
}

async function postComment() {
  if (!requireLogin()) return
  const content = commentText.value.trim()
  if (!content) {
    ElMessage.warning('请输入评论内容')
    return
  }
  posting.value = true
  try {
    const comment = await addComment(article.value.id, content)
    comments.value.unshift(comment)
    commentText.value = ''
    article.value.comments = (article.value.comments || 0) + 1
    ElMessage.success('评论成功')
  } finally {
    posting.value = false
  }
}

watch(
  () => route.params.id,
  () => {
    if (route.name === 'article') load()
  }
)

onMounted(load)
</script>

<style scoped>
.detail-page {
  padding-top: 20px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  color: var(--text-3);
  font-size: 13px;
}

.back {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--text-2);
}

.back:hover {
  color: var(--brand);
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 22px;
  align-items: start;
}

.article {
  padding: 34px 40px 26px;
}

.badges {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.badges .channel {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 6px;
  background: var(--brand-soft);
  color: var(--brand);
}

.badges .top {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 6px;
  background: var(--accent-soft);
  color: var(--accent);
}

.article-head h1 {
  margin: 0 0 18px;
  font-size: 30px;
  line-height: 1.45;
  letter-spacing: 0.3px;
}

.author-row {
  display: flex;
  align-items: center;
  gap: 11px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--line);
}

.author-row img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.author-info {
  display: flex;
  flex-direction: column;
  line-height: 1.35;
}

.author-info strong {
  font-size: 13px;
}

.author-info span {
  color: var(--text-3);
  font-size: 12px;
}

.follow {
  margin-left: auto;
}

.detail-cover {
  margin-top: 22px;
  border-radius: 12px;
  overflow: hidden;
}

.detail-cover img {
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  border-radius: 12px;
}

.detail-cover.triple {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.detail-cover.triple img {
  height: 180px;
}

.article-body {
  padding: 24px 0 8px;
  font-size: 16px;
  line-height: 1.95;
  color: #2c3242;
}

.article-body :deep(p) {
  margin: 0 0 18px;
}

.article-body :deep(h3) {
  font-size: 19px;
  margin: 26px 0 12px;
  padding-left: 12px;
  border-left: 4px solid var(--brand);
  line-height: 1.5;
}

.article-body :deep(img) {
  width: 100%;
  border-radius: 12px;
  margin: 6px 0 20px;
}

.article-body :deep(blockquote) {
  margin: 20px 0;
  padding: 14px 18px;
  border-radius: 10px;
  background: #f7f9fd;
  color: var(--text-2);
  font-size: 14px;
  border-left: 3px solid #cfdcff;
}

.article-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
}

.action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 999px;
  padding: 7px 16px;
  color: var(--text-2);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.18s;
}

.action:hover {
  border-color: #bfd2ff;
  color: var(--brand);
}

.action.like {
  background: #f7f9ff;
  border-color: #dbe6ff;
}

.action.like.active {
  background: var(--brand);
  border-color: var(--brand);
  color: #fff;
}

.action em {
  font-style: normal;
  opacity: 0.8;
}

.action-tip {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-3);
}

.aside {
  position: sticky;
  top: 88px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.author-card {
  padding: 24px;
  text-align: center;
}

.big-avatar {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  margin: 0 auto 10px;
}

.author-card h3 {
  margin: 0 0 4px;
  font-size: 16px;
}

.author-card > p {
  margin: 0 0 16px;
  color: var(--text-3);
  font-size: 12px;
}

.author-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 14px;
  border-top: 1px solid var(--line);
}

.author-stats div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-stats strong {
  font-size: 15px;
}

.author-stats span {
  font-size: 11px;
  color: var(--text-3);
}

.related {
  padding: 18px 20px;
}

.related h3 {
  margin: 0 0 14px;
  font-size: 14px;
}

.related-item {
  display: block;
  padding: 10px 0;
  border-top: 1px solid var(--line);
}

.related-item span {
  font-size: 13px;
  line-height: 1.55;
}

.related-item small {
  color: var(--text-3);
  font-size: 11px;
  margin-top: 4px;
  display: block;
}

.related-item:hover span {
  color: var(--brand);
}

.comments {
  margin-top: 22px;
  padding: 26px 34px 30px;
}

.comments-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 18px;
}

.comments-head h3 {
  margin: 0;
  font-size: 17px;
}

.comments-head h3 span {
  color: var(--brand);
  font-size: 13px;
  margin-left: 4px;
}

.sort {
  font-size: 12px;
  color: var(--text-3);
}

.comment-form {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.comment-form > img {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  flex-shrink: 0;
}

.input-wrap {
  flex: 1;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.login-hint {
  font-size: 12px;
  color: var(--text-3);
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.comment {
  display: flex;
  gap: 12px;
}

.comment > img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
}

.comment-main {
  flex: 1;
  border-bottom: 1px solid var(--line);
  padding-bottom: 14px;
}

.comment-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 4px;
}

.comment-head strong {
  font-size: 13px;
}

.comment-head span {
  font-size: 11px;
  color: var(--text-3);
}

.comment-main p {
  margin: 0;
  font-size: 14px;
  color: var(--text-2);
  line-height: 1.7;
}

.notfound {
  padding: 40px;
}

.loading-card {
  margin-bottom: 20px;
}

@media (max-width: 1000px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
  .aside {
    position: static;
  }
}

@media (max-width: 768px) {
  .article {
    padding: 22px 18px;
  }
  .article-head h1 {
    font-size: 22px;
  }
  .article-body {
    font-size: 15px;
  }
  .action-tip {
    display: none;
  }
  .comments {
    padding: 20px 18px;
  }
  .comments {
    margin-bottom: 70px;
  }
}
</style>
