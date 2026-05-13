export interface PaperItem {
  arxivId: string
  title: string
  authors: string[]
  abstract: string
  categories: string[]
  publishedDate: string
  arxivUrl: string
  pdfUrl: string
  source: string
  status: 'collected' | 'parsed' | 'deleted' | 'failed'
  hasPdf: boolean
  hasParsedDoc: boolean
  hasReport: boolean
  tags: string[]
  createdAt: string
}
