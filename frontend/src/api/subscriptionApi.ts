import http from './http'
import type { SubscriptionItem } from '../types/subscription'

export async function listSubscriptions(enabled?: boolean) {
  const params = enabled !== undefined ? { enabled } : {}
  const response = await http.get('/api/subscriptions', { params })
  return response.data
}

export async function getSubscription(id: number) {
  const response = await http.get(`/api/subscriptions/${id}`)
  return response.data
}

export async function createSubscription(data: Partial<SubscriptionItem>) {
  const response = await http.post('/api/subscriptions', data)
  return response.data
}

export async function updateSubscription(id: number, data: Partial<SubscriptionItem>) {
  const response = await http.put(`/api/subscriptions/${id}`, data)
  return response.data
}

export async function deleteSubscription(id: number) {
  const response = await http.delete(`/api/subscriptions/${id}`)
  return response.data
}

export async function runSubscriptionNow(id: number, dryRun = false) {
  const response = await http.post(`/api/subscriptions/${id}/run-now`, null, {
    params: { dry_run: dryRun },
  })
  return response.data
}
