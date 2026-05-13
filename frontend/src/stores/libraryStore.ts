import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  listPapers,
  deletePaper as deletePaperApi,
  getReport as getReportApi,
  deleteReport as deleteReportApi,
  regenerateReport as regenerateReportApi,
} from '../api/libraryApi'
import { parsePaper } from '../api/paperApi'
import { snakeToCamel } from '../utils/formatKeys'
import type { PaperItem } from '../types/paper'

export const useLibraryStore = defineStore('library', () => {
  const papers = ref<PaperItem[]>([])
  const loading = ref(false)
  const total = ref(0)
  const keyword = ref('')
  const currentReport = ref<string>('')
  const reportLoading = ref(false)

  async function fetchPapers(params: Record<string, any> = {}) {
    loading.value = true
    try {
      const data = await listPapers({ ...params, keyword: keyword.value })
      papers.value = snakeToCamel(data.papers || [])
      total.value = data.total || 0
    } finally {
      loading.value = false
    }
  }

  async function deletePaper(arxivId: string) {
    const result = await deletePaperApi(arxivId)
    if (result.success) {
      papers.value = papers.value.filter((p) => p.arxivId !== arxivId)
      total.value = Math.max(0, total.value - 1)
    }
    return result
  }

  async function parsePaperById(arxivId: string) {
    const result = await parsePaper(arxivId)
    if (result.success) {
      // Refresh paper list to show updated status
      await fetchPapers({ keyword: keyword.value })
    }
    return result
  }

  async function fetchReport(arxivId: string) {
    reportLoading.value = true
    try {
      const data = await getReportApi(arxivId)
      if (data.success) {
        currentReport.value = data.report_markdown || ''
      } else {
        currentReport.value = ''
      }
      return data
    } finally {
      reportLoading.value = false
    }
  }

  async function deleteReport(arxivId: string) {
    const result = await deleteReportApi(arxivId)
    if (result.success) {
      currentReport.value = ''
      await fetchPapers({ keyword: keyword.value })
    }
    return result
  }

  async function regenerateReport(arxivId: string) {
    reportLoading.value = true
    try {
      const result = await regenerateReportApi(arxivId)
      if (result.success) {
        await fetchPapers({ keyword: keyword.value })
      }
      return result
    } finally {
      reportLoading.value = false
    }
  }

  function setKeyword(kw: string) {
    keyword.value = kw
  }

  return {
    papers,
    loading,
    total,
    keyword,
    currentReport,
    reportLoading,
    fetchPapers,
    deletePaper,
    parsePaperById,
    fetchReport,
    deleteReport,
    regenerateReport,
    setKeyword,
  }
})
