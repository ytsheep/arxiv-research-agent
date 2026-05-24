const SNAKE_TO_CAMEL_MAP: Record<string, string> = {
  arxiv_id: 'arxivId',
  published_date: 'publishedDate',
  updated_date: 'updatedDate',
  arxiv_url: 'arxivUrl',
  pdf_url: 'pdfUrl',
  has_pdf: 'hasPdf',
  has_parsed_doc: 'hasParsedDoc',
  has_report: 'hasReport',
  created_at: 'createdAt',
  updated_at: 'updatedAt',
  summary_source: 'summarySource',
  core_problem: 'coreProblem',
  trace_id: 'traceId',
  task_type: 'taskType',
  user_input: 'userInput',
  error_message: 'errorMessage',
  started_at: 'startedAt',
  ended_at: 'endedAt',
  duration_ms: 'durationMs',
  error_code: 'errorCode',
  step_name: 'stepName',
  tool_name: 'toolName',
  reasoning_summary: 'reasoningSummary',
  input_summary: 'inputSummary',
  output_summary: 'outputSummary',
  candidate_k: 'candidateK',
  top_n: 'topN',
  cron_expr: 'cronExpr',
  email_enabled: 'emailEnabled',
  email_to: 'emailTo',
  feishu_enabled: 'feishuEnabled',
  feishu_webhook_ref: 'feishuWebhookRef',
  auto_parse_full_text: 'autoParseFullText',
  preferred_categories: 'preferredCategories',
  preferred_topics: 'preferredTopics',
  summary_language: 'summaryLanguage',
  default_candidate_k: 'defaultCandidateK',
  default_top_n: 'defaultTopN',
  paper_count: 'paperCount',
  sent_email: 'sentEmail',
  sent_feishu: 'sentFeishu',
  dry_run: 'dryRun',
  subscription_id: 'subscriptionId',
  run_date: 'runDate',
  selected_papers: 'selectedPapers',
  llm_provider: 'llmProvider',
  llm_model: 'llmModel',
  llm_api_key: 'llmApiKey',
  llm_api_key_set: 'llmApiKeySet',
  llm_available: 'llmAvailable',
  page_size: 'pageSize',
}

const CAMEL_TO_SNAKE_MAP: Record<string, string> = {}
for (const [snake, camel] of Object.entries(SNAKE_TO_CAMEL_MAP)) {
  CAMEL_TO_SNAKE_MAP[camel] = snake
}

export function camelToSnake<T>(obj: T): T {
  if (Array.isArray(obj)) {
    return obj.map(camelToSnake) as any
  }
  if (obj !== null && typeof obj === 'object') {
    const result: Record<string, any> = {}
    for (const [key, value] of Object.entries(obj as Record<string, any>)) {
      const newKey = CAMEL_TO_SNAKE_MAP[key] || key
      result[newKey] = camelToSnake(value)
    }
    return result as T
  }
  return obj
}

export function snakeToCamel<T>(obj: T): T {
  if (Array.isArray(obj)) {
    return obj.map(snakeToCamel) as any
  }
  if (obj !== null && typeof obj === 'object') {
    const result: Record<string, any> = {}
    for (const [key, value] of Object.entries(obj as Record<string, any>)) {
      const newKey = SNAKE_TO_CAMEL_MAP[key] || key
      result[newKey] = snakeToCamel(value)
    }
    return result as T
  }
  return obj
}
