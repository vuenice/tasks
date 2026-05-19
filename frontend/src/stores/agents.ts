import { defineStore } from 'pinia'
import { ref } from 'vue'
import { agentsApi, type Agent } from '@/api'

export const useAgentsStore = defineStore('agents', () => {
  const agents = ref<Agent[]>([])
  const loading = ref(false)

  async function fetchAgents() {
    loading.value = true
    try {
      agents.value = await agentsApi.list()
    } finally {
      loading.value = false
    }
  }

  async function createAgent(name: string) {
    const agent = await agentsApi.create(name)
    agents.value.push(agent)
    return agent
  }

  async function updateAgent(id: number, data: Partial<{ name: string; move_to_agent_id: number | null }>) {
    const updated = await agentsApi.update(id, data)
    const idx = agents.value.findIndex(a => a.id === id)
    if (idx !== -1) agents.value[idx] = updated
    return updated
  }

  async function deleteAgent(id: number) {
    await agentsApi.delete(id)
    agents.value = agents.value.filter(a => a.id !== id)
  }

  return { agents, loading, fetchAgents, createAgent, updateAgent, deleteAgent }
})
