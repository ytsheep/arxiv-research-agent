<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '../../types/chat'
import PaperCard from './PaperCard.vue'
import { formatTime } from '../../utils/formatTime'

const props = defineProps<{
  message: ChatMessage
}>()

const emit = defineEmits<{
  collect: [paper: any]
  parse: [paper: any]
}>()

const isUser = computed(() => props.message.role === 'user')
</script>

<template>
  <div class="message-bubble" :class="isUser ? 'user' : 'assistant'">
    <div class="bubble-content">
      <div class="message-text">{{ message.content }}</div>

      <div v-if="message.progress?.length" class="progress-list">
        <div
          v-for="event in message.progress"
          :key="event.eventId || `${event.eventType}-${event.timestamp}`"
          class="progress-item"
          :class="{ active: message.streaming && event === message.progress[message.progress.length - 1] }"
        >
          <span class="progress-dot"></span>
          <span>{{ event.message }}</span>
        </div>
      </div>

      <template v-if="message.papers && message.papers.length > 0">
        <div class="papers-list">
          <PaperCard
            v-for="paper in message.papers"
            :key="paper.arxivId"
            :paper="paper"
            @collect="emit('collect', $event)"
            @parse="emit('parse', $event)"
          />
        </div>
      </template>

      <div class="message-meta">
        <span class="time">{{ formatTime(message.timestamp) }}</span>
        <span v-if="message.traceId" class="trace-id">
          trace: {{ message.traceId }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-bubble {
  display: flex;
  margin-bottom: 16px;
}
.message-bubble.user {
  justify-content: flex-end;
}
.message-bubble.assistant {
  justify-content: flex-start;
}
.bubble-content {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
}
.user .bubble-content {
  background-color: #1a3a5c;
  border-bottom-right-radius: 4px;
}
.assistant .bubble-content {
  background-color: #2a2a2a;
  border-bottom-left-radius: 4px;
  min-width: 60%;
}
.message-text {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.papers-list {
  margin-top: 12px;
}
.progress-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #3a3a3a;
}
.progress-item {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #999;
  font-size: 12px;
}
.progress-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #67c23a;
  flex: 0 0 auto;
}
.progress-item.active {
  color: #d5e8ff;
}
.progress-item.active .progress-dot {
  background: #409eff;
}
.message-meta {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  font-size: 11px;
  color: #888;
}
</style>
