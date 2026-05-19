<template>
  <AppLayout>
    <div v-if="agent" class="flex flex-col h-full">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-800 shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-brand-600/20 border border-brand-600/30 flex items-center justify-center text-brand-400 font-bold text-sm">
            {{ agent.name[0].toUpperCase() }}
          </div>
          <div>
            <h1 class="font-semibold text-white leading-none">{{ agent.name }}</h1>
            <p v-if="agent.folderPath" class="text-xs text-gray-500 mt-0.5 truncate max-w-xs">{{ agent.folderPath }}</p>
          </div>
          <span v-if="agent.isDefault" class="text-xs px-2 py-0.5 rounded-full bg-brand-600/20 text-brand-400 border border-brand-600/30">default</span>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-gray-800 px-6 shrink-0 overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span class="flex items-center gap-1.5">
            <component :is="tab.icon" class="w-4 h-4" />
            {{ tab.label }}
          </span>
        </button>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-hidden">
        <Transition name="fade" mode="out-in">
          <TasksTab v-if="activeTab === 'tasks'" :key="'tasks-' + agentId" :agent-id="agentId" />
          <InstructionsTab v-else-if="activeTab === 'instructions'" :key="'inst-' + agentId" :agent="agent" />
          <SkillsTab v-else-if="activeTab === 'skills'" :key="'skills-' + agentId" :agent="agent" />
          <RoutineTab v-else-if="activeTab === 'routine'" :key="'routine-' + agentId" :agent="agent" />
        </Transition>
      </div>
    </div>

    <!-- Loading -->
    <div v-else class="flex-1 flex items-center justify-center">
      <div class="text-gray-500 text-sm">Loading agent…</div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, watch, defineAsyncComponent, h } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import TasksTab from '@/components/tabs/TasksTab.vue'
import InstructionsTab from '@/components/tabs/InstructionsTab.vue'
import SkillsTab from '@/components/tabs/SkillsTab.vue'
import RoutineTab from '@/components/tabs/RoutineTab.vue'
import { useAgentsStore } from '@/stores/agents'

// Tab icons as inline SVG render functions
const CheckSquareIcon = { render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '1.5' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' })
]) }
const DocIcon = { render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '1.5' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' })
]) }
const SparkleIcon = { render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '1.5' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z' })
]) }
const ClockIcon = { render: () => h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '1.5' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z' })
]) }

const route = useRoute()
const agentsStore = useAgentsStore()

const activeTab = ref('tasks')
const agentId = computed(() => Number(route.params.id))
const agent = computed(() => agentsStore.agents.find(a => a.id === agentId.value) ?? null)

const tabs = [
  { id: 'tasks', label: 'Tasks', icon: CheckSquareIcon },
  { id: 'instructions', label: 'Instructions', icon: DocIcon },
  { id: 'skills', label: 'Skills', icon: SparkleIcon },
  { id: 'routine', label: 'Routine', icon: ClockIcon },
]

// Reset tab when switching agents
watch(agentId, () => { activeTab.value = 'tasks' })
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
