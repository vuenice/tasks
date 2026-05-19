import { defineStore } from 'pinia'
import { ref } from 'vue'
import { routinesApi, type Routine } from '@/api'

export const useRoutinesStore = defineStore('routines', () => {
  const routines = ref<Routine[]>([])
  const loading = ref(false)
  const running = ref<Record<number, boolean>>({})

  async function fetchRoutines(agentId: number) {
    loading.value = true
    try {
      routines.value = await routinesApi.list(agentId)
    } finally {
      loading.value = false
    }
  }

  async function createRoutine(data: { agent_id: number; label: string; schedule?: string; description?: string }) {
    const r = await routinesApi.create({ ...data, is_active: true })
    routines.value.push(r)
    return r
  }

  async function updateRoutine(id: number, data: Partial<{ label: string; schedule: string; description: string; is_active: boolean }>) {
    const updated = await routinesApi.update(id, data)
    const idx = routines.value.findIndex(r => r.id === id)
    if (idx !== -1) routines.value[idx] = updated
    return updated
  }

  async function deleteRoutine(id: number) {
    await routinesApi.delete(id)
    routines.value = routines.value.filter(r => r.id !== id)
  }

  async function runNow(id: number) {
    running.value = { ...running.value, [id]: true }
    try {
      const result = await routinesApi.runNow(id)
      // Refresh last_run_at after execution
      setTimeout(async () => {
        const agentId = routines.value.find(r => r.id === id)?.agent_id
        if (agentId) await fetchRoutines(agentId)
      }, 1500)
      return result
    } finally {
      running.value = { ...running.value, [id]: false }
    }
  }

  return { routines, loading, running, fetchRoutines, createRoutine, updateRoutine, deleteRoutine, runNow }
})
