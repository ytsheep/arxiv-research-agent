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
  streaming?: boolean
  progress?: ChatProgressEvent[]
  metadata?: {
    comparison?: any
    selected_paper?: PaperCardItem
    survey_markdown?: string
    report_markdown?: string
    task_summary?: TaskSummaryItem[]
  }
}

export interface ChatProgressEvent {
  eventId: string
  eventType: string
  agent: string
  node: string
  taskId: string
  taskType: string
  status: string
  message: string
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
  metadata?: Record<string, any>
  error_code?: string
  detail?: string
}

export interface ChatTaskAccepted {
  success: boolean
  trace_id: string
  status: string
  stream_url: string
  result_url: string
}

export interface ComparisonResult {
  overview: string
  papers: { arxiv_id: string; title: string }[]
  dimensions: Record<string, string>
}

export interface TaskSummaryItem {
  task_id: string
  task_type: string
  status: 'completed' | 'failed' | 'skipped'
  summary: string
}
