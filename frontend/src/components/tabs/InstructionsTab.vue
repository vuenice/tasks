<template>
  <div class="h-full flex flex-col overflow-hidden">
    <div class="flex-1 overflow-y-auto px-6 py-5 space-y-5">

      <!-- After completion routing -->
      <div class="card space-y-3">
        <div>
          <h3 class="text-sm font-semibold text-white">After Completion</h3>
          <p class="text-xs text-gray-500 mt-0.5">When all tasks are done, hand off to another agent automatically.</p>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-400 whitespace-nowrap">After completion move to:</span>
          <select
            v-model="moveToAgentId"
            class="input flex-1"
            @change="onMoveToChange"
          >
            <option :value="null">— None —</option>
            <option
              v-for="a in otherAgents"
              :key="a.id"
              :value="a.id"
            >
              {{ a.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- CLAUDE.md editor -->
      <div class="flex flex-col flex-1 space-y-2">
        <div class="flex items-center justify-between">
          <div>
            <label class="label">Instructions <span class="text-gray-600 normal-case font-normal tracking-normal ml-1">(CLAUDE.md)</span></label>
            <p class="text-xs text-gray-500">These instructions are written to the agent's CLAUDE.md file.</p>
          </div>
          <button class="btn-primary text-xs px-3 py-1.5" :disabled="saving" @click="save">
            <svg v-if="saving" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
        <textarea
          v-model="content"
          class="textarea font-mono text-xs leading-relaxed"
          rows="18"
          placeholder="Write agent instructions in Markdown…&#10;&#10;# Agent Name&#10;&#10;## Role&#10;You are a helpful assistant that...&#10;&#10;## Behavior&#10;- Always respond in English&#10;- Keep answers concise"
          spellcheck="false"
        />
        <p v-if="saved" class="text-xs text-green-400 flex items-center gap-1">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Saved to CLAUDE.md
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { agentsApi, type Agent } from '@/api'
import { useAgentsStore } from '@/stores/agents'

const props = defineProps<{ agent: Agent }>()

const agentsStore = useAgentsStore()
const content = ref('')
const moveToAgentId = ref<number | null>(null)
const saving = ref(false)
const saved = ref(false)
let savedTimer: ReturnType<typeof setTimeout>

const otherAgents = computed(() => agentsStore.agents.filter(a => a.id !== props.agent.id))

async function load() {
  try {
    const data = await agentsApi.getInstructions(props.agent.id)
    content.value = data.content
    moveToAgentId.value = data.moveToAgentId ?? null
  } catch {
    content.value = ''
  }
}

async function save() {
  saving.value = true
  try {
    await agentsApi.updateInstructions(props.agent.id, content.value, moveToAgentId.value)
    saved.value = true
    clearTimeout(savedTimer)
    savedTimer = setTimeout(() => { saved.value = false }, 3000)
  } finally {
    saving.value = false
  }
}

async function onMoveToChange() {
  await agentsApi.updateInstructions(props.agent.id, content.value, moveToAgentId.value)
}

onMounted(load)
watch(() => props.agent.id, load)
</script>
