<template>
  <el-dialog
    v-model="visible"
    title="选择封面图片"
    width="860px"
    top="6vh"
    append-to-body
    destroy-on-close
  >
    <div class="picker-bar">
      <div class="tip">
        已选 <strong>{{ picks.length }}</strong> / {{ limit }} 张
        <span class="hint">支持从素材库选择，或上传新图片</span>
      </div>
      <el-upload :show-file-list="false" accept="image/*" :http-request="customUpload">
        <el-button type="primary" plain :loading="uploading">
          <el-icon><Upload /></el-icon>
          上传图片
        </el-button>
      </el-upload>
    </div>

    <div v-loading="loading" class="picker-grid">
      <button
        v-for="item in materials"
        :key="item.id"
        type="button"
        class="picker-item"
        :class="{ picked: picks.includes(item.url) }"
        @click="toggle(item)"
      >
        <img :src="item.url" alt="material" loading="lazy" />
        <span class="check">
          <el-icon><Check /></el-icon>
        </span>
      </button>
      <EmptyState
        v-if="!loading && materials.length === 0"
        title="素材库还是空的"
        description="上传第一张图片，开始创作吧"
      />
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="confirm">确定选择</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getMaterials, uploadMaterial } from '@/api/media'
import EmptyState from './EmptyState.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  limit: { type: Number, default: 1 },
  selected: { type: Array, default: () => [] }
})
const emit = defineEmits(['update:modelValue', 'confirm'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const materials = ref([])
const picks = ref([])
const loading = ref(false)
const uploading = ref(false)

watch(visible, (open) => {
  if (open) {
    picks.value = [...props.selected]
    load()
  }
})

async function load() {
  loading.value = true
  try {
    const data = await getMaterials({ page: 1, size: 60 })
    materials.value = data.records || []
  } finally {
    loading.value = false
  }
}

function toggle(item) {
  const index = picks.value.indexOf(item.url)
  if (index >= 0) {
    picks.value.splice(index, 1)
    return
  }
  if (picks.value.length >= props.limit) {
    if (props.limit === 1) {
      picks.value = [item.url]
      return
    }
    ElMessage.warning('最多选择 ' + props.limit + ' 张图片')
    return
  }
  picks.value.push(item.url)
}

async function customUpload(options) {
  uploading.value = true
  try {
    const material = await uploadMaterial(options.file)
    materials.value.unshift(material)
    if (picks.value.length < props.limit) {
      picks.value.push(material.url)
    }
    ElMessage.success('上传成功')
  } finally {
    uploading.value = false
  }
}

function confirm() {
  if (picks.value.length !== props.limit) {
    ElMessage.warning('请选择 ' + props.limit + ' 张图片')
    return
  }
  emit('confirm', [...picks.value])
  visible.value = false
}
</script>

<style scoped>
.picker-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.tip {
  font-size: 13px;
  color: var(--text-2);
}

.tip strong {
  color: var(--brand);
}

.hint {
  margin-left: 10px;
  color: var(--text-3);
  font-size: 12px;
}

.picker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  max-height: 52vh;
  overflow-y: auto;
  min-height: 120px;
}

.picker-item {
  position: relative;
  border: 2px solid transparent;
  border-radius: 10px;
  padding: 0;
  overflow: hidden;
  cursor: pointer;
  background: #f2f4f8;
  aspect-ratio: 16 / 9;
}

.picker-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.picker-item .check {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: transparent;
  display: grid;
  place-items: center;
  font-size: 13px;
}

.picker-item.picked {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(47, 107, 255, 0.16);
}

.picker-item.picked .check {
  background: var(--brand);
  color: #fff;
}
</style>
