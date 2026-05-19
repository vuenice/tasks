import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tasksApi, commentsApi, type Task, type Comment } from '@/api'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const currentAgentId = ref<number | null>(null)

  async function fetchTasks(agentId: number) {
    loading.value = true
    currentAgentId.value = agentId
    try {
      tasks.value = await tasksApi.list(agentId)
    } finally {
      loading.value = false
    }
  }

  async function createTask(agentId: number, title: string, description?: string, status: string = 'todo') {
    const task = await tasksApi.create({ agent_id: agentId, title, description, status })
    tasks.value.push(task)
    return task
  }

  async function updateTask(id: number, data: Partial<{ title: string; description: string; status: string; sort_order: number }>) {
    const updated = await tasksApi.update(id, data)
    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx !== -1) tasks.value[idx] = updated
    return updated
  }

  async function deleteTask(id: number) {
    await tasksApi.delete(id)
    tasks.value = tasks.value.filter(t => t.id !== id)
  }

  async function reorderTasks(updatedTasks: Array<{ id: number; status: string; sort_order: number }>) {
    await tasksApi.reorder(updatedTasks)
    for (const t of updatedTasks) {
      const idx = tasks.value.findIndex(tk => tk.id === t.id)
      if (idx !== -1) {
        tasks.value[idx].status = t.status as Task['status']
        tasks.value[idx].sortOrder = t.sort_order
        tasks.value[idx].sort_order = t.sort_order
      }
    }
  }

  async function addComment(taskId: number, content: string, author: 'user' | 'claude' = 'user') {
    const comment = await commentsApi.add(taskId, content, author)
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.comments = [...(task.comments ?? []), comment]
    }
    // Refresh after a short delay so the backend summary is ready
    setTimeout(() => refreshTask(taskId), 2800)
    return comment
  }

  async function deleteComment(taskId: number, commentId: number) {
    await commentsApi.delete(taskId, commentId)
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.comments = (task.comments ?? []).filter((c: Comment) => c.id !== commentId)
    }
    setTimeout(() => refreshTask(taskId), 2800)
  }

  async function refreshTask(taskId: number) {
    if (currentAgentId.value == null) return
    try {
      const all = await tasksApi.list(currentAgentId.value)
      const fresh = all.find(t => t.id === taskId)
      if (fresh) {
        const idx = tasks.value.findIndex(t => t.id === taskId)
        if (idx !== -1) tasks.value[idx] = fresh
      }
    } catch { /* ignore */ }
  }

  return {
    tasks, loading, currentAgentId,
    fetchTasks, createTask, updateTask, deleteTask, reorderTasks,
    addComment, deleteComment, refreshTask,
  }
})
