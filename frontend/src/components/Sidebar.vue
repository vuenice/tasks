<template>
  <aside class="w-64 flex flex-col bg-gray-950 border-r border-gray-800 h-full">
    <!-- Brand -->
    <div class="px-4 py-5 border-b border-gray-800">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg bg-brand-600/20 border border-brand-600/30 flex items-center justify-center">
          <svg class="w-4 h-4 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <span class="font-semibold text-white text-sm">{{ projectName }}</span>
      </div>
    </div>

    <!-- Agents list -->
    <div class="flex-1 overflow-y-auto py-3 px-2">
      <div class="px-2 mb-2">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Agents</span>
      </div>

      <TransitionGroup name="list" tag="div" class="space-y-0.5">
        <button
          v-for="agent in agentsStore.agents"
          :key="agent.id"
          class="sidebar-item w-full text-left"
          :class="{ active: isActive(agent.id) }"
          @click="goToAgent(agent.id)"
        >
          <div
            class="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0"
            :class="isActive(agent.id) ? 'bg-brand-600/30 text-brand-300' : 'bg-gray-700 text-gray-300'"
          >
            {{ agent.name[0].toUpperCase() }}
          </div>
          <span class="truncate flex-1">{{ agent.name }}</span>
          <span v-if="agent.isDefault" class="text-[10px] text-gray-600">default</span>
        </button>
      </TransitionGroup>

      <div v-if="agentsStore.loading" class="px-3 py-2 text-xs text-gray-600">
        Loading…
      </div>
    </div>

    <!-- New Agent Button -->
    <div class="px-3 pb-4 pt-2 border-t border-gray-800">
      <button class="btn-primary w-full justify-center" @click="showNewAgentModal = true">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Agent
      </button>
    </div>
  </aside>

  <!-- New Agent Modal -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="showNewAgentModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeModal" />
        <div class="relative bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-full max-w-sm p-6 space-y-5">
          <div>
            <h3 class="text-lg font-semibold text-white">New Agent</h3>
            <p class="text-sm text-gray-400 mt-1">A new folder with CLAUDE.md and SKILL.md will be created.</p>
          </div>

          <div>
            <label class="label">Agent Name</label>
            <input
              v-model="newAgentName"
              class="input"
              type="text"
              placeholder="Agent name…"
              @keyup.enter="createAgent"
              ref="nameInputRef"
              autofocus
            />
          </div>

          <div v-if="createError" class="text-sm text-red-400 bg-red-950/30 border border-red-800/30 rounded-lg px-3 py-2">
            {{ createError }}
          </div>

          <div class="flex gap-3 justify-end">
            <button class="btn-ghost" @click="closeModal">Cancel</button>
            <button class="btn-primary" :disabled="!newAgentName.trim() || creating" @click="createAgent">
              <svg v-if="creating" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ creating ? 'Creating…' : 'Create Agent' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgentsStore } from '@/stores/agents'
import { useSetupStore } from '@/stores/setup'

const route = useRoute()
const router = useRouter()
const agentsStore = useAgentsStore()
const setupStore = useSetupStore()

const showNewAgentModal = ref(false)
const newAgentName = ref('')
const creating = ref(false)
const createError = ref('')
const nameInputRef = ref<HTMLInputElement | null>(null)

const projectName = computed(() => setupStore.config?.project_name ?? 'Task Manager')

function isActive(id: number) {
  return route.params.id === String(id)
}

function goToAgent(id: number) {
  router.push({ name: 'agent', params: { id } })
}

function closeModal() {
  showNewAgentModal.value = false
  newAgentName.value = ''
  createError.value = ''
}

async function createAgent() {
  if (!newAgentName.value.trim() || creating.value) return
  creating.value = true
  createError.value = ''
  try {
    const agent = await agentsStore.createAgent(newAgentName.value.trim())
    closeModal()
    router.push({ name: 'agent', params: { id: agent.id } })
  } catch (e: any) {
    createError.value = e?.response?.data?.message ?? 'Failed to create agent'
  } finally {
    creating.value = false
  }
}

// Focus input when modal opens
const _watch = computed(() => showNewAgentModal.value)
import { watch } from 'vue'
watch(showNewAgentModal, async (val) => {
  if (val) {
    await nextTick()
    nameInputRef.value?.focus()
  }
})

onMounted(() => {
  agentsStore.fetchAgents()
})
</script>

<style scoped>
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95);
}
</style>
