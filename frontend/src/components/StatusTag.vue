<template>
  <span class="status-tag" :class="meta.type">{{ meta.text }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: Number, default: 0 }
})

const MAP = {
  0: { text: '草稿', type: 'draft' },
  1: { text: '待审核', type: 'pending' },
  2: { text: '审核通过', type: 'pass' },
  3: { text: '审核失败', type: 'fail' }
}

const meta = computed(() => MAP[props.status] || MAP[0])
</script>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 9px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-tag.draft {
  background: #f2f4f7;
  color: #667085;
}

.status-tag.pending {
  background: #fff7e6;
  color: #d97706;
}

.status-tag.pass {
  background: #e9f9ef;
  color: #16a34a;
}

.status-tag.fail {
  background: #fdecec;
  color: #dc2626;
}
</style>
