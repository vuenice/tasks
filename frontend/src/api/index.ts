import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Agent {
  id: number
  name: string
  folder_path: string | null
  // Legacy camelCase aliases kept for backwards-compat with existing components
  folderPath: string | null
  sort_order: number
  sortOrder: number
  is_default: boolean
  isDefault: boolean
  move_to_agent_id: number | null
  moveToAgentId: number | null
  created_at: string
  createdAt: string
  updated_at: string
  updatedAt: string
}

export interface Comment {
  id: number
  task_id: number
  content: string
  author: 'user' | 'claude'
  created_at: string
}

export interface Task {
  id: number
  agent_id: number
  // Legacy alias
  agentId: number
  title: string
  description: string | null
  status: 'todo' | 'in_progress' | 'done'
  summary: string | null
  sort_order: number
  sortOrder: number
  comments: Comment[]
  created_at: string
  createdAt: string
  updated_at: string
  updatedAt: string
}

export interface Routine {
  id: number
  agent_id: number
  label: string
  schedule: string | null
  description: string | null
  is_active: boolean
  last_run_at: string | null
  created_at: string
  updated_at: string
}

export interface SetupConfig {
  isSetup: boolean
  user_name?: string
  project_name?: string
  folder_path?: string
}

// ─── Normaliser — maps Python snake_case → camelCase ─────────────────────────

function normaliseAgent(a: any): Agent {
  return {
    ...a,
    folderPath: a.folder_path ?? a.folderPath ?? null,
    sortOrder: a.sort_order ?? a.sortOrder ?? 0,
    isDefault: a.is_default ?? a.isDefault ?? false,
    moveToAgentId: a.move_to_agent_id ?? a.moveToAgentId ?? null,
    createdAt: a.created_at ?? a.createdAt ?? '',
    updatedAt: a.updated_at ?? a.updatedAt ?? '',
  }
}

function normaliseTask(t: any): Task {
  const comments: Comment[] = (t.comments ?? []).map((c: any) => ({
    ...c,
    task_id: c.task_id ?? t.id,
  }))
  return {
    ...t,
    agentId: t.agent_id ?? t.agentId ?? 0,
    sortOrder: t.sort_order ?? t.sortOrder ?? 0,
    summary: t.summary ?? null,
    comments,
    createdAt: t.created_at ?? t.createdAt ?? '',
    updatedAt: t.updated_at ?? t.updatedAt ?? '',
  }
}

// ─── Setup ────────────────────────────────────────────────────────────────────

export const setupApi = {
  get: () => api.get<SetupConfig>('/setup').then(r => r.data),
  post: (data: { user_name: string; project_name: string; folder_path: string }) =>
    api.post('/setup', data).then(r => r.data),
}

// ─── Agents ───────────────────────────────────────────────────────────────────

export const agentsApi = {
  list: () => api.get<any[]>('/agents').then(r => r.data.map(normaliseAgent)),
  create: (name: string) => api.post<any>('/agents', { name }).then(r => normaliseAgent(r.data)),
  update: (id: number, data: Partial<{ name: string; move_to_agent_id: number | null }>) =>
    api.put<any>(`/agents/${id}`, data).then(r => normaliseAgent(r.data)),
  delete: (id: number) => api.delete(`/agents/${id}`).then(r => r.data),
  reorder: (order: number[]) => api.post('/agents/reorder', { order }).then(r => r.data),
  getInstructions: (id: number) =>
    api.get<{ content: string; moveToAgentId: number | null }>(`/agents/${id}/instructions`).then(r => r.data),
  updateInstructions: (id: number, content: string, move_to_agent_id?: number | null) =>
    api.put(`/agents/${id}/instructions`, { content, move_to_agent_id }).then(r => r.data),
  getSkills: (id: number) =>
    api.get<{ content: string }>(`/agents/${id}/skills`).then(r => r.data),
  updateSkills: (id: number, content: string) =>
    api.put(`/agents/${id}/skills`, { content }).then(r => r.data),
}

// ─── Tasks ────────────────────────────────────────────────────────────────────

export const tasksApi = {
  list: (agentId: number) =>
    api.get<any[]>('/tasks', { params: { agent_id: agentId } }).then(r => r.data.map(normaliseTask)),
  create: (data: { agent_id: number; title: string; description?: string; status?: string }) =>
    api.post<any>('/tasks', data).then(r => normaliseTask(r.data)),
  update: (id: number, data: Partial<{ title: string; description: string; status: string; sort_order: number; agent_id: number }>) =>
    api.put<any>(`/tasks/${id}`, data).then(r => normaliseTask(r.data)),
  delete: (id: number) => api.delete(`/tasks/${id}`).then(r => r.data),
  reorder: (tasks: Array<{ id: number; status: string; sort_order: number }>) =>
    api.post('/tasks/reorder', { tasks }).then(r => r.data),
}

// ─── Comments ─────────────────────────────────────────────────────────────────

export const commentsApi = {
  list: (taskId: number) =>
    api.get<Comment[]>(`/tasks/${taskId}/comments`).then(r => r.data),
  add: (taskId: number, content: string, author: 'user' | 'claude' = 'user') =>
    api.post<Comment>(`/tasks/${taskId}/comments`, { content, author }).then(r => r.data),
  delete: (taskId: number, commentId: number) =>
    api.delete(`/tasks/${taskId}/comments/${commentId}`).then(r => r.data),
}

// ─── Routines ─────────────────────────────────────────────────────────────────

export const routinesApi = {
  list: (agentId?: number) =>
    api.get<Routine[]>('/routines', { params: agentId != null ? { agent_id: agentId } : {} }).then(r => r.data),
  create: (data: { agent_id: number; label: string; schedule?: string; description?: string; is_active?: boolean }) =>
    api.post<Routine>('/routines', data).then(r => r.data),
  update: (id: number, data: Partial<{ label: string; schedule: string; description: string; is_active: boolean }>) =>
    api.put<Routine>(`/routines/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/routines/${id}`).then(r => r.data),
  runNow: (id: number) => api.post(`/routines/${id}/run`).then(r => r.data),
}

export default api
