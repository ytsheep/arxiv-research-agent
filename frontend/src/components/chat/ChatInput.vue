<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  send: [message: string]
}>()

const input = ref('')
const loading = defineProps<{ loading: boolean }>()

function handleSend() {
  const text = input.value.trim()
  if (!text) return
  emit('send', text)
  input.value = ''
}
</script>

<template>
  <div class="chat-input">
    <el-input
      v-model="input"
      type="textarea"
      :rows="2"
      placeholder="输入研究方向，例如：给我找 2 篇关于 agent 的论文"
      resize="none"
      @keydown.enter.exact.prevent="handleSend"
    />
    <el-button
      type="primary"
      :loading="loading"
      :disabled="!input.trim()"
      @click="handleSend"
    >
      发送
    </el-button>
  </div>
</template>

<style scoped>
.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: #1a1a1a;
  border-top: 1px solid #333;
  align-items: flex-end;
}
.chat-input :deep(.el-textarea__inner) {
  background-color: #2a2a2a;
  border-color: #444;
  color: #e0e0e0;
}
.chat-input :deep(.el-textarea__inner):focus {
  border-color: #409EFF;
}
</style>
