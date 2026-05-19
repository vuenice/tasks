<template>
  <div class="h-full flex flex-col overflow-hidden">
    <div class="flex-1 overflow-y-auto px-6 py-5 space-y-4">
      <div class="card space-y-2">
        <h3 class="text-sm font-semibold text-white">About Skills</h3>
        <p class="text-xs text-gray-400 leading-relaxed">
          Define the skills and capabilities available to this agent. This content is written to
          <code class="bg-gray-700 px-1 py-0.5 rounded text-gray-300">SKILL.md</code> in the agent's folder
          and can be referenced by Claude Code or other tools.
        </p>
      </div>

      <div class="flex flex-col space-y-2">
        <div class="flex items-center justify-between">
          <div>
            <label class="label">Skills <span class="text-gray-600 normal-case font-normal tracking-normal ml-1">(SKILL.md)</span></label>
            <p class="text-xs text-gray-500">Markdown content written to the agent's SKILL.md file.</p>
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
          rows="22"
          placeholder="Define skills in Markdown…&#10;&#10;# Skills&#10;&#10;## Web Search&#10;Use the web_search tool to look up current information.&#10;&#10;## Code Execution&#10;Run Python snippets to solve computational tasks."
          spellcheck="false"
        />

        <p v-if="saved" class="text-xs text-green-400 flex items-center gap-1">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Saved to SKILL.md
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { agentsApi, type Agent } from '@/api'

const props = defineProps<{ agent: Agent }>()

const content = ref('')
const saving = ref(false)
const saved = ref(false)
let savedTimer: ReturnType<typeof setTimeout>

async function load() {
  try {
    const data = await agentsApi.getSkills(props.agent.id)
    content.value = data.content
  } catch {
    content.value = ''
  }
}

async function save() {
  saving.value = true
  try {
    await agentsApi.updateSkills(props.agent.id, content.value)
    saved.value = true
    clearTimeout(savedTimer)
    savedTimer = setTimeout(() => { saved.value = false }, 3000)
  } finally {
    saving.value = false
  }
}

onMounted(load)
watch(() => props.agent.id, load)
</script>
