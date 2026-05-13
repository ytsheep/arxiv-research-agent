import { defineStore } from 'pinia'
import { ref } from 'vue'
import http from '../api/http'

export const useSettingsStore = defineStore('settings', () => {
  const preferences = ref<Record<string, string>>({})
  const loading = ref(false)
  const saving = ref(false)

  async function fetchPreferences() {
    loading.value = true
    try {
      const { data } = await http.get('/api/settings/preferences')
      if (data.success) {
        preferences.value = data.preferences || {}
      }
    } finally {
      loading.value = false
    }
  }

  async function savePreferences(updates: Record<string, any>) {
    saving.value = true
    try {
      const { data } = await http.put('/api/settings/preferences', updates)
      if (data.success) {
        Object.assign(preferences.value, updates)
      }
      return data
    } finally {
      saving.value = false
    }
  }

  function getInt(key: string, defaultVal: number): number {
    const v = preferences.value[key]
    return v ? parseInt(v, 10) || defaultVal : defaultVal
  }

  function getBool(key: string): boolean {
    return preferences.value[key] === 'true'
  }

  return {
    preferences,
    loading,
    saving,
    fetchPreferences,
    savePreferences,
    getInt,
    getBool,
  }
})
