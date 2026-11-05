<template>
  <div class="empty">
    <svg width="132" height="104" viewBox="0 0 132 104" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="18" y="16" width="96" height="66" rx="12" fill="#EEF3FF" />
      <rect x="30" y="30" width="52" height="6" rx="3" fill="#C7D7FF" />
      <rect x="30" y="44" width="72" height="6" rx="3" fill="#DCE6FF" />
      <rect x="30" y="58" width="60" height="6" rx="3" fill="#DCE6FF" />
      <circle cx="100" cy="74" r="20" fill="#FFFFFF" />
      <circle cx="100" cy="74" r="14" fill="#E8EFFF" />
      <path d="M100 67v14M93 74h14" stroke="#9DB7FF" stroke-width="3" stroke-linecap="round" />
    </svg>
    <p class="empty-title">{{ title }}</p>
    <p class="empty-desc">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '暂无内容' },
  description: { type: String, default: '换个筛选条件试试吧' }
})
</script>

<style scoped>
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 56px 20px;
  background: #fff;
  border-radius: var(--radius);
}

.empty-title {
  margin: 14px 0 4px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

.empty-desc {
  margin: 0 0 16px;
  font-size: 13px;
  color: var(--text-3);
}
</style>
