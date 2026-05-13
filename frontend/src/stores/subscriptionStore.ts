import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  listSubscriptions,
  createSubscription as createSubApi,
  updateSubscription as updateSubApi,
  deleteSubscription as deleteSubApi,
  runSubscriptionNow as runNowApi,
} from '../api/subscriptionApi'
import { snakeToCamel } from '../utils/formatKeys'
import type { SubscriptionItem } from '../types/subscription'

export const useSubscriptionStore = defineStore('subscription', () => {
  const subscriptions = ref<SubscriptionItem[]>([])
  const loading = ref(false)
  const running = ref<Set<number>>(new Set())

  async function fetchSubscriptions() {
    loading.value = true
    try {
      const data = await listSubscriptions()
      subscriptions.value = snakeToCamel(data.subscriptions || [])
    } finally {
      loading.value = false
    }
  }

  async function createSubscription(data: Partial<SubscriptionItem>) {
    const result = await createSubApi(data)
    if (result.success) {
      await fetchSubscriptions()
    }
    return result
  }

  async function updateSubscription(id: number, data: Partial<SubscriptionItem>) {
    const result = await updateSubApi(id, data)
    if (result.success) {
      await fetchSubscriptions()
    }
    return result
  }

  async function deleteSubscription(id: number) {
    const result = await deleteSubApi(id)
    if (result.success) {
      subscriptions.value = subscriptions.value.filter((s) => s.id !== id)
    }
    return result
  }

  async function runNow(id: number) {
    running.value.add(id)
    try {
      const result = await runNowApi(id)
      return result
    } finally {
      running.value.delete(id)
    }
  }

  return {
    subscriptions,
    loading,
    running,
    fetchSubscriptions,
    createSubscription,
    updateSubscription,
    deleteSubscription,
    runNow,
  }
})
