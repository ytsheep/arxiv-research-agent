export interface SubscriptionItem {
  id: number
  name: string
  topics: string[]
  categories: string[]
  candidateK: number
  topN: number
  cronExpr: string
  timezone: string
  emailEnabled: boolean
  emailTo: string
  feishuEnabled: boolean
  feishuWebhookRef: string
  autoParseFullText: boolean
  enabled: boolean
  createdAt: string
  updatedAt: string
}
