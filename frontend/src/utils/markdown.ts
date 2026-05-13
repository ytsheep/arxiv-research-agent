import { marked } from 'marked'

export function renderMarkdown(text: string): string {
  if (!text) return ''
  return marked(text) as string
}
