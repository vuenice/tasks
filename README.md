# Task Manager — Python + Vue

A task manager where Claude automatically executes scheduled tasks, posts results as comments, and maintains an AI-generated summary of each task's progress.

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.10+ · FastAPI · SQLAlchemy · APScheduler |
| Frontend | Vue 3 · TypeScript · Tailwind CSS · Vite |
| AI execution | `claude -p` CLI (Claude Code) via subprocess |
| Database | SQLite (`database/taskmanager.db`) |

---

## Quick start

### 1. Backend

```bash
cd task-manager/backend-python

# Install dependencies (once)
pip install -r requirements.txt

# Start the API server on :3333
uvicorn main:app --reload --port 3333
# Windows: double-click start.bat
```

### 2. Frontend

```bash
cd task-manager/frontend
npm install
npm run dev   # → http://localhost:5173
```

---

## How automated execution works

1. **Create a routine** in the Routine tab for an agent and set a cron schedule
   (e.g. `0 9 * * *` = every day at 9 AM).

2. **APScheduler** runs in the background inside the FastAPI process.
   At the scheduled time it calls `execute_routine(routine_id)`.

3. **For every active task** (todo / in_progress) belonging to that agent:
   - Reads `CLAUDE.md` (agent instructions) and `SKILL.md` (available skills) from the agent folder.
   - Calls `claude -p "<full prompt>" --no-permission-prompts` via shell — no human interaction needed.
   - Saves the Claude response as a `claude`-authored comment on the task.
   - Re-runs summarisation: all comments are fed to Claude which writes a 2-3 sentence summary stored in `task.summary`.

4. The Vue UI shows the live summary on each task card and in the detail panel side-bar.

---

## CLAUDE.md / SKILL.md

Each agent has its own folder (configured during first-run Setup).

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Standing instructions — *how* Claude should behave for this agent |
| `SKILL.md` | Available tools, APIs, or capabilities Claude can use |

Both files are editable via the **Instructions** and **Skills** tabs.
They are injected verbatim into every automated execution prompt so Claude always has full context and never needs to ask questions.

---

## API reference

```
GET  /api/health
GET/POST /api/setup

GET/POST       /api/agents
GET/PUT/DELETE /api/agents/:id
GET/PUT        /api/agents/:id/instructions
GET/PUT        /api/agents/:id/skills
POST           /api/agents/reorder

GET/POST       /api/tasks
GET/PUT/DELETE /api/tasks/:id
POST           /api/tasks/reorder

GET            /api/tasks/:id/comments
POST           /api/tasks/:id/comments   ← triggers auto-summarise
DELETE         /api/tasks/:id/comments/:cid

GET/POST       /api/routines
PUT/DELETE     /api/routines/:id
POST           /api/routines/:id/run     ← manual trigger
```
