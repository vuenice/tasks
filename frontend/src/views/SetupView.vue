<template>
  <div class="min-h-screen bg-gray-950 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo / Title -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-600/20 border border-brand-600/30 mb-5">
          <svg class="w-8 h-8 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">Task Manager</h1>
        <p class="text-gray-400 text-sm">Let's set up your workspace in a few quick steps</p>
      </div>

      <!-- Steps -->
      <div class="flex justify-center gap-2 mb-8">
        <div v-for="i in 3" :key="i"
          class="h-1 w-12 rounded-full transition-all duration-300"
          :class="step >= i ? 'bg-brand-500' : 'bg-gray-700'" />
      </div>

      <!-- Step 1: Your Name -->
      <Transition name="slide" mode="out-in">
        <div v-if="step === 1" key="step1" class="card space-y-5">
          <div>
            <h2 class="text-lg font-semibold text-white mb-1">What's your name?</h2>
            <p class="text-sm text-gray-400">This creates your default personal agent.</p>
          </div>
          <div>
            <label class="label">Your Name</label>
            <input
              v-model="form.user_name"
              class="input"
              type="text"
              placeholder="e.g. Yogesh"
              @keyup.enter="form.user_name && step++"
              autofocus
            />
          </div>
          <div class="flex justify-end">
            <button class="btn-primary" :disabled="!form.user_name.trim()" @click="step++">
              Continue
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Step 2: Project Name -->
        <div v-else-if="step === 2" key="step2" class="card space-y-5">
          <div>
            <h2 class="text-lg font-semibold text-white mb-1">Name your project</h2>
            <p class="text-sm text-gray-400">Give this workspace a meaningful name.</p>
          </div>
          <div>
            <label class="label">Project Name</label>
            <input
              v-model="form.project_name"
              class="input"
              type="text"
              placeholder="e.g. My AI Agents"
              @keyup.enter="form.project_name && step++"
              autofocus
            />
          </div>
          <div class="flex justify-between">
            <button class="btn-ghost" @click="step--">Back</button>
            <button class="btn-primary" :disabled="!form.project_name.trim()" @click="step++">
              Continue
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Step 3: Folder -->
        <div v-else-if="step === 3" key="step3" class="card space-y-5">
          <div>
            <h2 class="text-lg font-semibold text-white mb-1">Agents folder</h2>
            <p class="text-sm text-gray-400">Where should agent folders be created on your system?</p>
          </div>
          <div>
            <label class="label">Folder Path</label>
            <input
              v-model="form.folder_path"
              class="input"
              type="text"
              placeholder="e.g. C:\Users\Yogesh\Agents or /home/yogesh/agents"
              autofocus
            />
            <p class="mt-1.5 text-xs text-gray-500">
              Each new agent will get a subfolder here containing CLAUDE.md and SKILL.md
            </p>
          </div>
          <div v-if="error" class="text-sm text-red-400 bg-red-950/30 border border-red-800/30 rounded-lg px-3 py-2">
            {{ error }}
          </div>
          <div class="flex justify-between">
            <button class="btn-ghost" @click="step--">Back</button>
            <button class="btn-primary" :disabled="!form.folder_path.trim() || submitting" @click="submit">
              <svg v-if="submitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ submitting ? 'Creating...' : 'Get Started' }}
              <svg v-if="!submitting" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSetupStore } from '@/stores/setup'

const router = useRouter()
const setupStore = useSetupStore()

const step = ref(1)
const submitting = ref(false)
const error = ref('')

const form = ref({
  user_name: '',
  project_name: '',
  folder_path: '',
})

async function submit() {
  if (!form.value.folder_path.trim()) return
  submitting.value = true
  error.value = ''
  try {
    await setupStore.submit(form.value)
    router.push({ name: 'home' })
  } catch (e: any) {
    error.value = e?.response?.data?.message ?? 'Something went wrong. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
}
.slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
