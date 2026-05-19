import { defineStore } from 'pinia'
import { ref } from 'vue'
import { setupApi, type SetupConfig } from '@/api'

export const useSetupStore = defineStore('setup', () => {
  const isSetup = ref(false)
  const loaded = ref(false)
  const config = ref<SetupConfig | null>(null)

  async function load() {
    try {
      const data = await setupApi.get()
      config.value = data
      isSetup.value = data.isSetup
    } catch {
      isSetup.value = false
    } finally {
      loaded.value = true
    }
  }

  async function submit(data: { user_name: string; project_name: string; folder_path: string }) {
    const result = await setupApi.post(data)
    config.value = { isSetup: true, ...data }
    isSetup.value = true
    return result
  }

  return { isSetup, loaded, config, load, submit }
})
