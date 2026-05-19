<template>
  <div class="task-card group" @click="$emit('open')">
    <div class="flex items-start gap-3">
      <!-- Drag handle -->
      <div class="mt-0.5 text-gray-600 group-hover:text-gray-400 transition-colors cursor-grab shrink-0">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <circle cx="9" cy="6" r="1.5"/><circle cx="15" cy="6" r="1.5"/>
          <circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/>
          <circle cx="9" cy="18" r="1.5"/><circle cx="15" cy="18" r="1.5"/>
        </svg>
      </div>

      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-gray-100 leading-snug">{{ task.title }}</p>

        <!-- AI Summary (if available) -->
        <p v-if="task.summary" class="text-xs text-brand-400/80 mt-1 line-clamp-2 italic">
          {{ task.summary }}
        </p>
        <!-- Fallback description -->
        <p v-else-if="task.description" class="text-xs text-gray-500 mt-1 line-clamp-2">
          {{ task.description }}
        </p>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" @click.stop>
        <button
          v-if="task.status === 'todo'"
          class="p-1.5 rounded-lg text-gray-500 hover:text-yellow-400 hover:bg-yellow-400/10 transition-all"
          title="Move to In Progress"
          @click="$emit('move-to-progress')"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
        <button
          v-if="task.status === 'in_progress'"
          class="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-700 transition-all"
          title="Move back to Todo"
          @click="$emit('move-to-todo')"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 15l-3-3m0 0l3-3m-3 3h8M3 12a9 9 0 1118 0 9 9 0 01-18 0z" />
          </svg>
        </button>
        <button
          class="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-700 transition-all"
          title="Edit"
          @click="$emit('edit')"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          class="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-400/10 transition-all"
          title="Delete"
          @click="$emit('delete')"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Footer: status + comment count -->
    <div class="mt-3 flex items-center gap-2">
      <span
        class="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full font-medium"
        :class="task.status === 'in_progress'
          ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
          : 'bg-gray-700/50 text-gray-500 border border-gray-700'"
      >
        <span class="w-1.5 h-1.5 rounded-full" :class="task.status === 'in_progress' ? 'bg-yellow-400' : 'bg-gray-600'" />
        {{ task.status === 'in_progress' ? 'In Progress' : 'To Do' }}
      </span>

      <!-- Comment count badge -->
      <button
        v-if="commentCount > 0"
        class="ml-auto inline-flex items-center gap-1 text-[11px] text-gray-500 hover:text-gray-300 transition-colors"
        @click.stop="$emit('open')"
      >
        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-3 3v-3z" />
        </svg>
        {{ commentCount }}
      </button>

      <!-- AI badge when summary present -->
      <span
        v-if="task.summary"
        class="inline-flex items-center gap-0.5 text-[10px] text-brand-400/60 ml-auto"
      >
        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
        </svg>
        AI
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '@/api'

const props = defineProps<{ task: Task }>()
defineEmits(['open', 'edit', 'delete', 'move-to-progress', 'move-to-todo'])

const commentCount = computed(() => props.task.comments?.length ?? 0)
</script>
