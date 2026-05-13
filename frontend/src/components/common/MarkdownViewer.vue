<script setup lang="ts">
import { computed } from 'vue'
import { renderMarkdown } from '../../utils/markdown'

const props = defineProps<{
  content: string
}>()

const html = computed(() => renderMarkdown(props.content))
</script>

<template>
  <div class="markdown-viewer" v-html="html" />
</template>

<style scoped>
.markdown-viewer {
  font-size: 14px;
  line-height: 1.8;
  color: #ccc;
}
.markdown-viewer :deep(h1) { font-size: 22px; margin-top: 16px; }
.markdown-viewer :deep(h2) { font-size: 18px; margin-top: 14px; }
.markdown-viewer :deep(h3) { font-size: 16px; margin-top: 12px; }
.markdown-viewer :deep(p) { margin: 8px 0; }
.markdown-viewer :deep(code) {
  background-color: #2a2a2a;
  padding: 2px 6px;
  border-radius: 3px;
}
</style>
