<template>
  <div class="simple-page page">
    <div class="card">
      <div class="head">
        <h1>校园视频</h1>
        <p>用镜头记录运动会、晚会与校园日常</p>
      </div>
      <EmptyState title="视频频道正在建设中" description="校园短视频即将上线，先去图文频道看看吧">
        <el-button type="primary" round @click="$router.push('/')">去看图文</el-button>
      </EmptyState>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.simple-page {
  padding-top: 24px;
  max-width: 900px;
}
.card {
  padding: 28px 32px;
}
.head h1 {
  margin: 0 0 6px;
  font-size: 22px;
}
.head p {
  margin: 0 0 8px;
  color: var(--text-3);
  font-size: 13px;
}
</style>
