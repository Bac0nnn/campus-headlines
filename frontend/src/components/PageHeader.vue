<template>
  <div class="page-header">
    <div>
      <h2>{{ title }}</h2>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
    <div class="actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' }
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 18px;
  gap: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
}

.page-header p {
  margin: 4px 0 0;
  color: var(--text-3);
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>
