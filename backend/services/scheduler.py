"""
APScheduler service for automated routine execution.

Key functions:
  start(db)          — called on app startup; loads all active routines from DB
  register_routine(r) — add / replace a job for a Routine ORM object
  unregister_routine(id) — remove a job by routine id
  execute_routine(id) — the actual job function (also callable via /run endpoint)

Job flow for each routine trigger:
  1. Load routine + agent from DB
  2. Read CLAUDE.md and SKILL.md from the agent's folder
  3. For every active task (todo | in_progress) belonging to that agent,
     call `claude -p` with a prompt built from CLAUDE.md + SKILL.md + task info
  4. Save the result as a Claude comment on the task
  5. Trigger comment summarisation for the task
  6. Update routine.last_run_at
"""
import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# Single shared scheduler instance
scheduler = BackgroundScheduler(
    job_defaults={"coalesce": True, "max_instances": 1, "misfire_grace_time": 300}
)


# ── Lifecycle ──────────────────────────────────────────────────────────────────

def start(db=None):
    """
    Start the scheduler and register all currently active routines.
    Call this once from the FastAPI lifespan startup hook.
    """
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")

    # Re-import here to avoid circular imports at module load
    if db is None:
        from database import SessionLocal
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        from models import Routine
        routines = db.query(Routine).filter_by(is_active=True).all()
        for r in routines:
            register_routine(r)
        logger.info("Registered %d routine(s) from DB", len(routines))
    finally:
        if close_db:
            db.close()


def stop():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")


# ── Job management ─────────────────────────────────────────────────────────────

def register_routine(routine) -> bool:
    """
    Add or replace an APScheduler job for *routine*.
    Returns True if registered, False if the schedule is missing/invalid.
    """
    if not routine.schedule:
        return False

    job_id = f"routine_{routine.id}"
    try:
        trigger = CronTrigger.from_crontab(routine.schedule)
        scheduler.add_job(
            execute_routine,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            args=[routine.id],
        )
        logger.info(
            "Scheduled routine %d ('%s') → cron '%s'",
            routine.id, routine.label, routine.schedule,
        )
        return True
    except Exception as exc:
        logger.error("Cannot register routine %d: %s", routine.id, exc)
        return False


def unregister_routine(routine_id: int):
    """Remove a job from the scheduler (if it exists)."""
    job_id = f"routine_{routine_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info("Removed scheduler job for routine %d", routine_id)


# ── Execution ─────────────────────────────────────────────────────────────────

def execute_routine(routine_id: int):
    """
    Called by APScheduler (or the /run endpoint).

    Runs all active tasks belonging to the routine's agent through Claude,
    posts results as comments, and re-summarises each task.
    """
    from database import SessionLocal
    from models import Routine, Agent, Task, Comment
    from services.claude_service import run_task_with_claude, summarize_comments

    db = SessionLocal()
    try:
        routine = db.query(Routine).get(routine_id)
        if not routine:
            logger.warning("execute_routine: routine %d not found", routine_id)
            return

        agent = db.query(Agent).get(routine.agent_id)
        if not agent:
            logger.warning("execute_routine: agent %d not found", routine.agent_id)
            return

        logger.info(
            "Executing routine %d ('%s') for agent '%s'",
            routine_id, routine.label, agent.name,
        )

        # ── Read CLAUDE.md and SKILL.md ──────────────────────────────────────
        claude_md, skill_md = "", ""
        if agent.folder_path:
            for fname, attr in (("CLAUDE.md", "claude_md"), ("SKILL.md", "skill_md")):
                path = os.path.join(agent.folder_path, fname)
                try:
                    with open(path, encoding="utf-8") as fh:
                        if attr == "claude_md":
                            claude_md = fh.read()
                        else:
                            skill_md = fh.read()
                except OSError:
                    pass

        # ── Iterate active tasks ──────────────────────────────────────────────
        tasks = (
            db.query(Task)
            .filter(
                Task.agent_id == agent.id,
                Task.status.in_(["todo", "in_progress"]),
            )
            .all()
        )

        if not tasks:
            logger.info("No active tasks for agent '%s' — nothing to do", agent.name)
        else:
            cwd = agent.folder_path or "."
            for task in tasks:
                # Run the task with Claude
                report = run_task_with_claude(
                    task.title,
                    task.description or "",
                    claude_md,
                    skill_md,
                    cwd=cwd,
                )

                # Save result as a Claude comment
                comment = Comment(
                    task_id=task.id,
                    content=report,
                    author="claude",
                )
                db.add(comment)
                db.flush()

                # Re-summarise
                all_comments = (
                    db.query(Comment)
                    .filter_by(task_id=task.id)
                    .order_by(Comment.created_at)
                    .all()
                )
                texts = [f"[{c.author}] {c.content}" for c in all_comments]
                task.summary = summarize_comments(task.title, texts)

        # ── Update last_run_at ────────────────────────────────────────────────
        routine.last_run_at = datetime.utcnow()
        db.commit()
        logger.info("Routine %d ('%s') completed", routine_id, routine.label)

    except Exception as exc:
        db.rollback()
        logger.error("execute_routine %d failed: %s", routine_id, exc, exc_info=True)
    finally:
        db.close()
