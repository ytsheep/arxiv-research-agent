import http from './http'

export async function listTraces(params: Record<string, any> = {}) {
  const response = await http.get('/api/traces', { params })
  return response.data
}

export async function getTrace(traceId: string) {
  const response = await http.get(`/api/traces/${traceId}`)
  return response.data
}
