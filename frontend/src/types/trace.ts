export interface TraceStep {
  stepName: string
  toolName: string | null
  inputSummary: string
  outputSummary: string
  status: string
  startedAt: string
  endedAt: string
  durationMs: number | null
  errorMessage: string
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
