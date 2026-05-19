"""
Comments router.

POST /api/tasks/{task_id}/comments
  → saves comment
  → triggers async summarization via Claude CLI
  → updates task.summary
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["comments"])


def _refresh_summary(task_id: int):
    """
    Background job: read all comments for this task, ask Claude to summarise
    them, and update task.summary.  Uses a fresh DB session so it is safe to
    run off the request thread.
    """
    from database import SessionLocal
    from services.claude_service import summarize_comments

    db = SessionLocal()
    try:
        task = db.query(models.Task).get(task_id)
        if not task:
            return

        comments = (
            db.query(models.Comment)
            .filter_by(task_id=task_id)
            .order_by(models.Comment.created_at)
            .all()
        )
        if not comments:
            return

        texts = [f"[{c.author}] {c.content}" for c in comments]
        summary = summarize_comments(task.title, texts)
        task.summary = summary
        db.commit()
        logger.info("Summary updated for task %d", task_id)
    except Exception as exc:
        logger.error("summarise_comments failed for task %d: %s", task_id, exc)
    finally:
        db.close()


@router.get("/{task_id}/comments", response_model=List[schemas.CommentOut])
def list_comments(task_id: int, db: Session = Depends(get_db)):
    if not db.query(models.Task).get(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return (
        db.query(models.Comment)
        .filter_by(task_id=task_id)
        .order_by(models.Comment.created_at)
        .all()
    )


@router.post("/{task_id}/comments", response_model=schemas.CommentOut)
def add_comment(
    task_id: int,
    body: schemas.CommentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if not db.query(models.Task).get(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    comment = models.Comment(
        task_id=task_id,
        content=body.content,
        author=body.author or "user",
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Kick off summarisation in background (non-blocking)
    background_tasks.add_task(_refresh_summary, task_id)

    return comment


@router.delete("/{task_id}/comments/{comment_id}")
def delete_comment(
    task_id: int,
    comment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    comment = (
        db.query(models.Comment)
        .filter_by(id=comment_id, task_id=task_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()

    # Re-summarise after deletion
    background_tasks.add_task(_refresh_summary, task_id)

    return {"success": True}
