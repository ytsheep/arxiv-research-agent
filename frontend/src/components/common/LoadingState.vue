<script setup lang="ts">
defineProps<{
  text?: string
}>()
</script>

<template>
  <div class="loading-state">
    <el-icon class="loading-icon" :size="32"><Loading /></el-icon>
    <p>{{ text || '加载中...' }}</p>
  </div>
</template>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #888;
}
.loading-icon {
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
