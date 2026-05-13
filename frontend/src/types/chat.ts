export interface PaperCardItem {
  arxivId: string
  title: string
  authors: string[]
  publishedDate: string
  categories: string[]
  arxivUrl: string
  pdfUrl: string
  summary: string
  coreProblem: string
  method: string
  result: string
  summarySource: 'metadata_only' | 'abstract_intro' | 'full_text'
  actions: string[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  papers?: PaperCardItem[]
  traceId?: string
  timestamp: string
}

export interface ChatRequest {
  session_id: string
  message: string
}

export interface ChatResponse {
  success: boolean
  type: string
  trace_id: string
  message: string
  papers: PaperCardItem[]
  error_code?: string
  detail?: string
}
