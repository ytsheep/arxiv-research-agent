import http from './http'

export async function collectPaper(arxivId: string, paper: any) {
  const response = await http.post(`/api/papers/${arxivId}/collect`, { paper })
  return response.data
}

export async function parsePaper(arxivId: string) {
  const response = await http.post(`/api/papers/${arxivId}/parse`)
  return response.data
}
