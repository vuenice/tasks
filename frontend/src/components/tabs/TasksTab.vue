<template>
  <div class="h-full flex overflow-hidden">

    <!-- ── Kanban board ─────────────────────────────────────────────────────── -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Toolbar -->
      <div class="flex items-center justify-between px-6 py-3 border-b border-gray-800 shrink-0">
        <span class="text-sm text-gray-400">
          {{ todoTasks.length + inProgressTasks.length }} active tasks
        </span>
        <button class="btn-primary text-xs px-3 py-1.5" @click="showAddTask = true">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Task
        </button>
      </div>

      <!-- Columns -->
      <div class="flex-1 overflow-hidden flex gap-0">
        <!-- TODO -->
        <div class="flex-1 flex flex-col border-r border-gray-800 overflow-hidden">
          <div class="flex items-center gap-2 px-4 py-3 shrink-0">
            <div class="w-2 h-2 rounded-full bg-gray-500" />
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider">To Do</span>
            <span class="ml-auto text-xs text-gray-600 bg-gray-800 rounded-full px-2 py-0.5">{{ todoTasks.length }}</span>
          </div>
          <div class="flex-1 overflow-y-auto px-3 pb-4">
            <draggable v-model="todoTasksDraggable" group="tasks" item-key="id" :animation="150"
              ghost-class="ghost-card" drag-class="drag-card" class="space-y-2 min-h-[60px]"
              @end="onDragEnd">
              <template #item="{ element }">
                <TaskCard :task="element"
                  @open="openDetail(element)"
                  @edit="openEdit(element)"
                  @delete="deleteTask(element.id)"
                  @move-to-progress="moveTask(element, 'in_progress')" />
              </template>
            </draggable>
            <div v-if="todoTasks.length === 0 && !tasksStore.loading"
              class="flex flex-col items-center justify-center py-10 text-center">
              <div class="w-10 h-10 rounded-xl bg-gray-800 flex items-center justify-center mb-3">
                <svg class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p class="text-xs text-gray-600">No tasks yet</p>
            </div>
          </div>
        </div>

        <!-- IN PROGRESS -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <div class="flex items-center gap-2 px-4 py-3 shrink-0">
            <div class="w-2 h-2 rounded-full bg-yellow-500" />
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider">In Progress</span>
            <span class="ml-auto text-xs text-gray-600 bg-gray-800 rounded-full px-2 py-0.5">{{ inProgressTasks.length }}</span>
          </div>
          <div class="flex-1 overflow-y-auto px-3 pb-4">
            <draggable v-model="inProgressTasksDraggable" group="tasks" item-key="id" :animation="150"
              ghost-class="ghost-card" drag-class="drag-card" class="space-y-2 min-h-[60px]"
              @end="onDragEnd">
              <template #item="{ element }">
                <TaskCard :task="element"
                  @open="openDetail(element)"
                  @edit="openEdit(element)"
                  @delete="deleteTask(element.id)"
                  @move-to-todo="moveTask(element, 'todo')" />
              </template>
            </draggable>
            <div v-if="inProgressTasks.length === 0 && !tasksStore.loading"
              class="flex flex-col items-center justify-center py-10 text-center">
              <div class="w-10 h-10 rounded-xl bg-gray-800 flex items-center justify-center mb-3">
                <svg class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <p class="text-xs text-gray-600">Nothing in progress</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Task Detail Side Panel ───────────────────────────────────────────── -->
    <Transition name="slide">
      <div v-if="detailTask" class="w-80 flex flex-col border-l border-gray-800 bg-gray-950 overflow-hidden shrink-0">
        <!-- Panel header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-800 shrink-0">
          <h3 class="text-sm font-semibold text-white truncate flex-1 mr-2">{{ detailTask.title }}</h3>
          <button class="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-all"
            @click="detailTask = null">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto">
          <!-- Description -->
          <div v-if="detailTask.description" class="px-4 pt-4">
            <p class="text-xs text-gray-500 leading-relaxed">{{ detailTask.description }}</p>
          </div>

          <!-- AI Summary -->
          <div v-if="detailTask.summary" class="mx-4 mt-4 p-3 rounded-xl bg-brand-600/10 border border-brand-600/20">
            <div class="flex items-center gap-1.5 mb-1.5">
              <svg class="w-3.5 h-3.5 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
              <span class="text-[11px] font-semibold text-brand-400 uppercase tracking-wider">AI Summary</span>
            </div>
            <p class="text-xs text-brand-300/80 leading-relaxed">{{ detailTask.summary }}</p>
          </div>

          <!-- Comments -->
          <div class="px-4 pt-4 pb-2">
            <div class="flex items-center gap-1.5 mb-3">
              <svg class="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-3 3v-3z" />
              </svg>
              <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Comments</span>
              <span class="text-xs text-gray-600">({{ detailTask.comments?.length ?? 0 }})</span>
            </div>

            <!-- Comment list -->
            <div v-if="detailTask.comments?.length" class="space-y-3 mb-4">
              <div v-for="comment in detailTask.comments" :key="comment.id"
                class="group/comment flex gap-2">
                <!-- Avatar -->
                <div class="w-6 h-6 rounded-full shrink-0 flex items-center justify-center text-[10px] font-bold mt-0.5"
                  :class="comment.author === 'claude'
                    ? 'bg-brand-600/20 text-brand-400 border border-brand-600/30'
                    : 'bg-gray-700 text-gray-300'">
                  {{ comment.author === 'claude' ? 'AI' : 'U' }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-baseline gap-2">
                    <span class="text-[11px] font-semibold"
                      :class="comment.author === 'claude' ? 'text-brand-400' : 'text-gray-300'">
                      {{ comment.author === 'claude' ? 'Claude' : 'You' }}
                    </span>
                    <span class="text-[10px] text-gray-600">{{ formatDate(comment.created_at) }}</span>
                  </div>
                  <p class="text-xs text-gray-400 mt-0.5 leading-relaxed whitespace-pre-wrap break-words">
                    {{ comment.content }}
                  </p>
                </div>
                <!-- Delete comment -->
                <button
                  class="opacity-0 group-hover/comment:opacity-100 p-1 rounded text-gray-600 hover:text-red-400 transition-all shrink-0"
                  @click="removeComment(comment.id)">
                  <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div v-else class="py-4 text-center">
              <p class="text-xs text-gray-600">No comments yet</p>
              <p class="text-[11px] text-gray-700 mt-1">Add one below — Claude will auto-summarise</p>
            </div>

            <!-- Add comment input -->
            <div class="border-t border-gray-800 pt-3">
              <textarea
                v-model="newComment"
                class="textarea text-xs"
                rows="2"
                placeholder="Add a comment…"
                @keydown.ctrl.enter="submitComment"
                @keydown.meta.enter="submitComment"
              />
              <div class="flex items-center justify-between mt-2">
                <span class="text-[10px] text-gray-700">Ctrl+Enter to send</span>
                <button
                  class="btn-primary text-xs px-3 py-1.5"
                  :disabled="!newComment.trim() || submittingComment"
                  @click="submitComment">
                  {{ submittingComment ? '…' : 'Comment' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── Add / Edit Task Modal ────────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showAddTask || editingTask" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeTaskModal" />
          <div class="relative bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-4">
            <h3 class="text-lg font-semibold text-white">{{ editingTask ? 'Edit Task' : 'Add Task' }}</h3>

            <div>
              <label class="label">Title</label>
              <input v-model="taskForm.title" class="input" type="text" placeholder="Task title"
                @keyup.enter="saveTask" autofocus />
            </div>
            <div>
              <label class="label">Description <span class="text-gray-600 normal-case font-normal">(optional)</span></label>
              <textarea v-model="taskForm.description" class="textarea" rows="3" placeholder="More details…" />
            </div>
            <div>
              <label class="label">Status</label>
              <select v-model="taskForm.status" class="input">
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
              </select>
            </div>

            <div class="flex gap-3 justify-end pt-1">
              <button class="btn-ghost" @click="closeTaskModal">Cancel</button>
              <button v-if="editingTask" class="btn-danger mr-auto"
                @click="deleteTask(editingTask!.id); closeTaskModal()">Delete</button>
              <button class="btn-primary" :disabled="!taskForm.title.trim() || saving" @click="saveTask">
                {{ saving ? 'Saving…' : (editingTask ? 'Save Changes' : 'Add Task') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import draggable from 'vuedraggable'
import TaskCard from '@/components/TaskCard.vue'
import { useTasksStore } from '@/stores/tasks'
import type { Task } from '@/api'

const props = defineProps<{ agentId: number }>()
const tasksStore = useTasksStore()

// ── Task lists ─────────────────────────────────────────────────────────────

const todoTasks = computed(() =>
  tasksStore.tasks.filter(t => t.status === 'todo')
    .sort((a, b) => (a.sort_order ?? a.sortOrder) - (b.sort_order ?? b.sortOrder)))

const inProgressTasks = computed(() =>
  tasksStore.tasks.filter(t => t.status === 'in_progress')
    .sort((a, b) => (a.sort_order ?? a.sortOrder) - (b.sort_order ?? b.sortOrder)))

// Writable computed refs for vuedraggable
const todoTasksDraggable = computed({
  get: () => [...todoTasks.value],
  set: () => { /* handled by onDragEnd */ },
})
const inProgressTasksDraggable = computed({
  get: () => [...inProgressTasks.value],
  set: () => { /* handled by onDragEnd */ },
})

// ── Detail panel ───────────────────────────────────────────────────────────

const detailTask = ref<Task | null>(null)
const newComment = ref('')
const submittingComment = ref(false)

// Keep detail panel in sync when the store refreshes
watch(
  () => tasksStore.tasks,
  (tasks) => {
    if (detailTask.value) {
      const fresh = tasks.find(t => t.id === detailTask.value!.id)
      if (fresh) detailTask.value = fresh
    }
  },
  { deep: true }
)

function openDetail(task: Task) {
  detailTask.value = task
  newComment.value = ''
}

async function submitComment() {
  if (!newComment.value.trim() || !detailTask.value) return
  submittingComment.value = true
  try {
    await tasksStore.addComment(detailTask.value.id, newComment.value.trim())
    newComment.value = ''
  } finally {
    submittingComment.value = false
  }
}

async function removeComment(commentId: number) {
  if (!detailTask.value) return
  await tasksStore.deleteComment(detailTask.value.id, commentId)
}

function formatDate(iso: string) {
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

// ── Add/Edit modal ─────────────────────────────────────────────────────────

const showAddTask = ref(false)
const editingTask = ref<Task | null>(null)
const saving = ref(false)
const taskForm = ref({ title: '', description: '', status: 'todo' })

function openEdit(task: Task) {
  editingTask.value = task
  taskForm.value = { title: task.title, description: task.description ?? '', status: task.status }
}

function closeTaskModal() {
  showAddTask.value = false
  editingTask.value = null
  taskForm.value = { title: '', description: '', status: 'todo' }
}

async function saveTask() {
  if (!taskForm.value.title.trim()) return
  saving.value = true
  try {
    if (editingTask.value) {
      await tasksStore.updateTask(editingTask.value.id, {
        title: taskForm.value.title,
        description: taskForm.value.description || undefined,
        status: taskForm.value.status,
      })
    } else {
      await tasksStore.createTask(props.agentId, taskForm.value.title, taskForm.value.description || undefined, taskForm.value.status)
    }
    closeTaskModal()
  } finally {
    saving.value = false
  }
}

async function deleteTask(id: number) {
  if (detailTask.value?.id === id) detailTask.value = null
  await tasksStore.deleteTask(id)
}

async function moveTask(task: Task, newStatus: 'todo' | 'in_progress') {
  await tasksStore.updateTask(task.id, { status: newStatus })
}

async function onDragEnd() {
  const allTasks = tasksStore.tasks
  const updates: Array<{ id: number; status: string; sort_order: number }> = []
  allTasks
    .filter(t => t.status === 'todo')
    .sort((a, b) => (a.sort_order ?? a.sortOrder) - (b.sort_order ?? b.sortOrder))
    .forEach((t, i) => updates.push({ id: t.id, status: 'todo', sort_order: i }))
  allTasks
    .filter(t => t.status === 'in_progress')
    .sort((a, b) => (a.sort_order ?? a.sortOrder) - (b.sort_order ?? b.sortOrder))
    .forEach((t, i) => updates.push({ id: t.id, status: 'in_progress', sort_order: i }))
  if (updates.length) await tasksStore.reorderTasks(updates)
}

onMounted(() => tasksStore.fetchTasks(props.agentId))
watch(() => props.agentId, id => tasksStore.fetchTasks(id))
</script>

<style scoped>
.ghost-card { opacity: 0.4; border: 2px dashed #4a5cff !important; }
.drag-card { transform: rotate(2deg); box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
.slide-enter-active, .slide-leave-active { transition: width 0.22s ease, opacity 0.22s ease; }
.slide-enter-from, .slide-leave-to { width: 0; opacity: 0; overflow: hidden; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
