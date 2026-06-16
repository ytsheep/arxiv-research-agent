import axios from 'axios'
import http from './http'
import { snakeToCamel } from '../utils/formatKeys'
import type {
  ChatProgressEvent,
  ChatRequest,
  ChatResponse,
  ChatTaskAccepted,
} from '../types/chat'

const CHAT_REQUEST_TIMEOUT_MS = 180_000

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await http.post<ChatResponse>('/api/chat', request, {
    timeout: CHAT_REQUEST_TIMEOUT_MS,
  })
  return response.data
}

export async function sendMessageStream(
  request: ChatRequest,
  onProgress: (event: ChatProgressEvent, traceId: string) => void,
): Promise<ChatResponse> {
  const acceptedResponse = await http.post<ChatTaskAccepted>('/api/chat/tasks', request)
  const accepted = acceptedResponse.data
  const baseUrl = String(http.defaults.baseURL || '').replace(/\/$/, '')
  const source = new EventSource(`${baseUrl}${accepted.stream_url}`)

  onProgress({
    eventId: '',
    eventType: 'workflow.accepted',
    agent: '',
    node: '',
    taskId: '',
    taskType: '',
    status: 'accepted',
    message: '任务已接收，正在启动 Agent 工作流',
    timestamp: new Date().toISOString(),
  }, accepted.trace_id)

  return new Promise((resolve) => {
    source.onmessage = (messageEvent) => {
      const raw = JSON.parse(messageEvent.data)
      const event = snakeToCamel<ChatProgressEvent>(raw)
      onProgress(event, accepted.trace_id)

      if (
        event.eventType === 'workflow.completed'
        || event.eventType === 'workflow.partial'
        || event.eventType === 'workflow.failed'
      ) {
        source.close()
        const response = raw.payload?.response || {
          success: event.eventType === 'workflow.completed',
          type: event.eventType === 'workflow.completed' ? 'workflow_result' : 'error',
          trace_id: accepted.trace_id,
          message: event.message,
          papers: [],
        }
        response.papers = snakeToCamel(response.papers || [])
        resolve(response as ChatResponse)
      }
    }

    source.onerror = () => {
      onProgress({
        eventId: '',
        eventType: 'connection.retrying',
        agent: '',
        node: '',
        taskId: '',
        taskType: '',
        status: 'running',
        message: '进度连接暂时中断，正在自动重连',
        timestamp: new Date().toISOString(),
      }, accepted.trace_id)
    }
  })
}

export function getChatRequestErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return '请求失败，请稍后重试。'
  }

  if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
    return '任务执行超过 3 分钟，后端可能仍在运行，请稍后到流程查询页查看结果。'
  }

  if (!error.response) {
    return '无法连接后端服务，请确认后端已启动。'
  }

  const detail = error.response.data?.message || error.response.data?.detail
  return detail ? `请求失败：${detail}` : `请求失败，服务端返回状态码 ${error.response.status}。`
}
