import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getChatRequestErrorMessage, sendMessageStream } from '../api/chatApi'
import type { ChatMessage, ChatProgressEvent } from '../types/chat'

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

  function addStreamingMessage(): string {
    const id = generateId()
    messages.value.push({
      id,
      role: 'assistant',
      content: '任务已接收，正在启动 Agent 工作流',
      traceId: '',
      timestamp: new Date().toISOString(),
      streaming: true,
      progress: [],
    })
    return id
  }

  function updateStreamingMessage(messageId: string, event: ChatProgressEvent, traceId: string) {
    const message = messages.value.find((item) => item.id === messageId)
    if (!message) return
    message.traceId = traceId
    if (event.eventType !== 'heartbeat') {
      message.content = event.message
      const duplicate = message.progress?.some((item) =>
        (item.eventId && item.eventId === event.eventId)
        || (item.eventType === event.eventType && item.message === event.message)
      )
      if (!duplicate) {
        message.progress = [...(message.progress || []), event]
      }
    }
  }

  async function sendChatMessage(content: string) {
    addUserMessage(content)
    const streamingMessageId = addStreamingMessage()
    loading.value = true

    try {
      const response = await sendMessageStream(
        {
          session_id: sessionId.value,
          message: content,
        },
        (event, traceId) => updateStreamingMessage(streamingMessageId, event, traceId),
      )
      const text = response.message || '收到回复'
      const message = messages.value.find((item) => item.id === streamingMessageId)
      if (message) {
        message.content = text
        message.papers = response.papers || []
        message.traceId = response.trace_id
        message.streaming = false
        message.metadata = response.metadata
      }
    } catch (error: unknown) {
      const message = messages.value.find((item) => item.id === streamingMessageId)
      if (message) {
        message.content = getChatRequestErrorMessage(error)
        message.streaming = false
      }
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
