import http from './http'
import type { ChatRequest, ChatResponse } from '../types/chat'

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await http.post<ChatResponse>('/api/chat', request)
  return response.data
}
