import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listTraces, getTrace } from '../api/traceApi'
import { snakeToCamel } from '../utils/formatKeys'
import type { TraceItem } from '../types/trace'

export const useTraceStore = defineStore('trace', () => {
  const traces = ref<TraceItem[]>([])
  const currentTrace = ref<TraceItem | null>(null)
  const loading = ref(false)
  const total = ref(0)

  async function fetchTraces(params: Record<string, any> = {}) {
    loading.value = true
    try {
      const data = await listTraces(params)
      traces.value = snakeToCamel(data.traces || [])
      total.value = data.total || 0
    } finally {
      loading.value = false
    }
  }

  async function fetchTraceDetail(traceId: string) {
    loading.value = true
    try {
      const data = await getTrace(traceId)
      currentTrace.value = snakeToCamel(data.trace)
    } finally {
      loading.value = false
    }
  }

  return {
    traces,
    currentTrace,
    loading,
    total,
    fetchTraces,
    fetchTraceDetail,
  }
})
