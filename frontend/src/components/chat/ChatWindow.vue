<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../../stores/chatStore'
import MessageBubble from './MessageBubble.vue'
import ChatInput from './ChatInput.vue'
import { collectPaper, parsePaper } from '../../api/paperApi'
import { ElMessage } from 'element-plus'
import type { PaperCardItem } from '../../types/chat'

const chatStore = useChatStore()
const router = useRouter()
const messagesContainer = ref<HTMLElement>()
const collectingPaper = ref<Set<string>>(new Set())
const parsingPaper = ref<Set<string>>(new Set())

async function handleSend(message: string) {
  await chatStore.sendChatMessage(message)
  scrollToBottom()
}

async function handleCollect(paper: PaperCardItem) {
  const arxivId = paper.arxivId
  if (collectingPaper.value.has(arxivId)) return

  collectingPaper.value.add(arxivId)
  try {
    const result = await collectPaper(arxivId, paper)
    if (result.success) {
      ElMessage.success(`论文 ${arxivId} 已收藏`)
    } else {
      ElMessage.error(result.message || '收藏失败')
    }
  } catch {
    ElMessage.error('收藏请求失败，请检查后端服务')
  } finally {
    collectingPaper.value.delete(arxivId)
  }
}

async function handleParse(paper: PaperCardItem) {
  const arxivId = paper.arxivId
  if (parsingPaper.value.has(arxivId)) return

  parsingPaper.value.add(arxivId)
  try {
    const result = await parsePaper(arxivId)
    if (result.success) {
      ElMessage.success({
        message: `解析完成！trace: ${result.trace_id}`,
        duration: 3000,
      })
    } else {
      ElMessage.error(result.message || '解析失败，请确认论文已收藏')
    }
  } catch {
    ElMessage.error('解析请求失败，请检查后端服务')
  } finally {
    parsingPaper.value.delete(arxivId)
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

onMounted(() => {
  if (chatStore.messages.length === 0) {
    chatStore.messages.push({
      id: 'welcome',
      role: 'assistant',
      content: '你好！我是 arXiv 论文助手。\n\n你可以输入研究方向搜索论文，例如：\n"给我找 2 篇关于 agent 的论文"\n"帮我推荐 3 篇最新的 RAG 方向论文"',
      timestamp: new Date().toISOString(),
    })
  }
})
</script>

<template>
  <div class="chat-window">
    <div ref="messagesContainer" class="messages-container">
      <MessageBubble
        v-for="msg in chatStore.messages"
        :key="msg.id"
        :message="msg"
        @collect="handleCollect"
        @parse="handleParse"
      />
    </div>
    <ChatInput :loading="chatStore.loading" @send="handleSend" />
  </div>
</template>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 900px;
  margin: 0 auto;
}
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}
</style>
