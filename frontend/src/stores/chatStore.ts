import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessage } from '../api/chatApi'
import type { ChatMessage, PaperCardItem } from '../types/chat'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const sessionId = ref(`session_${Date.now()}`)

  function generateId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
  }

  function addUserMessage(content: string) {
    messages.value.push({
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    })
  }

  function addAssistantMessage(content: string, papers: PaperCardItem[] = [], traceId: string = '') {
    messages.value.push({
      id: generateId(),
      role: 'assistant',
      content,
      papers,
      traceId,
      timestamp: new Date().toISOString(),
    })
  }

  async function sendChatMessage(content: string) {
    addUserMessage(content)
    loading.value = true

    try {
      const response = await sendMessage({
        session_id: sessionId.value,
        message: content,
      })

      const text = response.message || '收到回复'
      addAssistantMessage(text, response.papers || [], response.trace_id)
    } catch (error: any) {
      addAssistantMessage('请求失败，请检查后端服务是否已启动。')
    } finally {
      loading.value = false
    }
  }

  return {
    messages,
    loading,
    sessionId,
    sendChatMessage,
  }
})
