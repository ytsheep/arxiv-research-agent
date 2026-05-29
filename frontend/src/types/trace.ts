export interface TraceStep {
  stepName: string
  toolName: string | null
  reasoningSummary: string
  inputSummary: string
  outputSummary: string
  status: string
  startedAt: string
  endedAt: string
  durationMs: number | null
  errorMessage: string
  agentName?: string
  stepType?: string
  messageType?: string
}

export interface TraceItem {
  traceId: string
  taskType: string
  userInput: string
  summary: string
  tags: string[]
  status: string
  startedAt: string
  endedAt: string
  durationMs: number | null
  errorMessage: string
  steps: TraceStep[]
}
