import http from './http'

export async function listPapers(params: Record<string, any> = {}) {
  const response = await http.get('/api/library/papers', { params })
  return response.data
}

export async function getPaper(arxivId: string) {
  const response = await http.get(`/api/library/papers/${arxivId}`)
  return response.data
}

export async function deletePaper(arxivId: string, hard: boolean = false) {
  const response = await http.delete(`/api/library/papers/${arxivId}`, {
    params: { hard },
  })
  return response.data
}

export async function getReport(arxivId: string) {
  const response = await http.get(`/api/library/papers/${arxivId}/report`)
  return response.data
}

export async function deleteReport(arxivId: string) {
  const response = await http.delete(`/api/library/papers/${arxivId}/report`)
  return response.data
}

export async function regenerateReport(arxivId: string) {
  const response = await http.post(`/api/library/papers/${arxivId}/report/regenerate`)
  return response.data
}
