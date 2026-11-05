<template>
  <div class="channel-nav">
    <button
      v-for="item in items"
      :key="String(item.id)"
      class="channel"
      :class="{ active: item.id === modelValue }"
      @click="select(item.id)"
    >
      {{ item.name }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  channels: { type: Array, default: () => [] },
  modelValue: { type: Number, default: null }
})
const emit = defineEmits(['update:modelValue'])

const items = computed(() => [{ id: null, name: '推荐' }, ...props.channels])

function select(id) {
  emit('update:modelValue', id)
}
</script>

<style scoped>
.channel-nav {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 4px 0 10px;
  scrollbar-width: none;
}

.channel-nav::-webkit-scrollbar {
  display: none;
}

.channel {
  flex-shrink: 0;
  border: 0;
  background: transparent;
  color: var(--text-2);
  font-size: 15px;
  padding: 7px 14px;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.18s;
}

.channel:hover {
  color: var(--brand);
  background: var(--brand-soft);
}

.channel.active {
  color: #fff;
  background: linear-gradient(135deg, #2f6bff, #5b8bff);
  font-weight: 600;
  box-shadow: 0 6px 16px rgba(47, 107, 255, 0.28);
}
</style>
