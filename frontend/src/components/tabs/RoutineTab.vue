<template>
  <div class="h-full flex flex-col overflow-hidden">
    <div class="flex-1 overflow-y-auto px-6 py-5 space-y-4">

      <!-- Header -->
      <div class="card space-y-3">
        <div class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-xl bg-purple-600/20 border border-purple-600/30 flex items-center justify-center shrink-0">
            <svg class="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-white">Scheduled Routines</h3>
            <p class="text-xs text-gray-400 mt-0.5 leading-relaxed">
              Define cron schedules. Claude will run all active tasks for this agent automatically — reading CLAUDE.md + SKILL.md, executing without questions, and posting results as comments.
            </p>
          </div>
        </div>
      </div>

      <!-- Cron reference -->
      <div class="flex items-start gap-3 px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700/50">
        <svg class="w-4 h-4 text-gray-400 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="text-xs text-gray-400 space-y-0.5">
          <p class="font-medium text-gray-300">Cron format: <code class="text-brand-400">min hr day month weekday</code></p>
          <p><code class="text-gray-300">0 9 * * *</code> — every day at 9am &nbsp;·&nbsp; <code class="text-gray-300">0 9 * * 1</code> — every Monday 9am</p>
          <p><code class="text-gray-300">0 */2 * * *</code> — every 2 hours &nbsp;·&nbsp; <code class="text-gray-300">*/30 * * * *</code> — every 30 min</p>
        </div>
      </div>

      <!-- Existing routines -->
      <div v-if="routinesStore.loading" class="text-center py-6 text-sm text-gray-600">Loading…</div>

      <div v-else-if="routinesStore.routines.length > 0" class="space-y-2">
        <div v-for="r in routinesStore.routines" :key="r.id"
          class="card group/card">
          <div class="flex items-start gap-3">
            <!-- Active indicator -->
            <button
              class="mt-0.5 w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-all"
              :class="r.is_active ? 'bg-purple-600/20 border border-purple-600/30 text-purple-400' : 'bg-gray-700/50 border border-gray-700 text-gray-600'"
              :title="r.is_active ? 'Active — click to pause' : 'Paused — click to activate'"
              @click="toggleActive(r)">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  :d="r.is_active
                    ? 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z'
                    : 'M10 9v6m4-6v6'" />
              </svg>
            </button>

            <div class="flex-1 min-w-0">
              <!-- Edit inline or display -->
              <template v-if="editingId === r.id">
                <input v-model="editForm.label" class="input text-sm mb-2" placeholder="Label" />
                <input v-model="editForm.schedule" class="input text-xs mb-2 font-mono" placeholder="Cron: 0 9 * * *" />
                <textarea v-model="editForm.description" class="textarea text-xs mb-2" rows="2" placeholder="What should Claude do?" />
                <div class="flex gap-2">
                  <button class="btn-primary text-xs px-3 py-1" @click="saveEdit(r.id)">Save</button>
                  <button class="btn-ghost text-xs px-3 py-1" @click="editingId = null">Cancel</button>
                </div>
              </template>
              <template v-else>
                <p class="text-sm font-medium text-gray-100">{{ r.label }}</p>
                <p v-if="r.schedule" class="text-xs text-purple-400 font-mono mt-0.5">{{ r.schedule }}</p>
                <p v-if="r.description" class="text-xs text-gray-500 mt-1 line-clamp-2">{{ r.description }}</p>
                <p v-if="r.last_run_at" class="text-[11px] text-gray-600 mt-1">
                  Last run: {{ formatDate(r.last_run_at) }}
                </p>
              </template>
            </div>

            <!-- Actions -->
            <div v-if="editingId !== r.id" class="flex items-center gap-1 opacity-0 group-hover/card:opacity-100 transition-opacity shrink-0">
              <!-- Run now -->
              <button
                class="p-1.5 rounded-lg text-gray-500 hover:text-green-400 hover:bg-green-400/10 transition-all"
                :title="routinesStore.running[r.id] ? 'Running…' : 'Run now'"
                :disabled="routinesStore.running[r.id]"
                @click="runNow(r.id)">
                <svg class="w-3.5 h-3.5" :class="{ 'animate-spin': routinesStore.running[r.id] }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    :d="routinesStore.running[r.id]
                      ? 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
                      : 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664zM21 12a9 9 0 11-18 0 9 9 0 0118 0z'" />
                </svg>
              </button>
              <!-- Edit -->
              <button
                class="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-700 transition-all"
                title="Edit"
                @click="startEdit(r)">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <!-- Delete -->
              <button
                class="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-400/10 transition-all"
                title="Delete"
                @click="deleteRoutine(r.id)">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!routinesStore.loading" class="text-center py-6">
        <p class="text-xs text-gray-600">No routines yet. Add one below.</p>
      </div>

      <!-- Add routine form -->
      <div class="card space-y-4">
        <h4 class="text-sm font-semibold text-white">Add Routine</h4>

        <div>
          <label class="label">Label</label>
          <input v-model="form.label" class="input" type="text" placeholder="e.g. Daily standup" />
        </div>
        <div>
          <label class="label">Schedule <span class="text-gray-600 font-normal normal-case">(cron)</span></label>
          <input v-model="form.schedule" class="input font-mono text-sm" type="text" placeholder="0 9 * * *" />
        </div>
        <div>
          <label class="label">Instructions <span class="text-gray-600 font-normal normal-case">(optional)</span></label>
          <textarea v-model="form.description" class="textarea" rows="3"
            placeholder="What should Claude do? Leave blank to use CLAUDE.md instructions." />
        </div>

        <div class="flex justify-end">
          <button class="btn-primary text-xs px-3 py-1.5" :disabled="!form.label.trim() || adding" @click="addRoutine">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            {{ adding ? 'Adding…' : 'Add Routine' }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { Agent, Routine } from '@/api'
import { useRoutinesStore } from '@/stores/routines'

const props = defineProps<{ agent: Agent }>()
const routinesStore = useRoutinesStore()

// ── Form state ─────────────────────────────────────────────────────────────

const form = ref({ label: '', schedule: '', description: '' })
const adding = ref(false)
const editingId = ref<number | null>(null)
const editForm = ref({ label: '', schedule: '', description: '' })

// ── Lifecycle ──────────────────────────────────────────────────────────────

onMounted(() => routinesStore.fetchRoutines(props.agent.id))
watch(() => props.agent.id, id => routinesStore.fetchRoutines(id))

// ── Actions ────────────────────────────────────────────────────────────────

async function addRoutine() {
  if (!form.value.label.trim()) return
  adding.value = true
  try {
    await routinesStore.createRoutine({
      agent_id: props.agent.id,
      label: form.value.label,
      schedule: form.value.schedule || undefined,
      description: form.value.description || undefined,
    })
    form.value = { label: '', schedule: '', description: '' }
  } finally {
    adding.value = false
  }
}

function startEdit(r: Routine) {
  editingId.value = r.id
  editForm.value = { label: r.label, schedule: r.schedule ?? '', description: r.description ?? '' }
}

async function saveEdit(id: number) {
  await routinesStore.updateRoutine(id, {
    label: editForm.value.label,
    schedule: editForm.value.schedule || undefined,
    description: editForm.value.description || undefined,
  })
  editingId.value = null
}

async function toggleActive(r: Routine) {
  await routinesStore.updateRoutine(r.id, { is_active: !r.is_active })
}

async function deleteRoutine(id: number) {
  await routinesStore.deleteRoutine(id)
}

async function runNow(id: number) {
  await routinesStore.runNow(id)
}

function formatDate(iso: string | null) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  return d.toLocaleDateString()
}
</script>
