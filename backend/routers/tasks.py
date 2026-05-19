from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[schemas.TaskOut])
def list_tasks(agent_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    q = (
        db.query(models.Task)
        .options(joinedload(models.Task.comments))
        .order_by(models.Task.sort_order, models.Task.created_at)
    )
    if agent_id is not None:
        q = q.filter(models.Task.agent_id == agent_id)
    return q.all()


@router.post("", response_model=schemas.TaskOut)
def create_task(body: schemas.TaskCreate, db: Session = Depends(get_db)):
    # Verify agent exists
    if not db.query(models.Agent).get(body.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    count = db.query(models.Task).filter_by(agent_id=body.agent_id).count()
    task = models.Task(
        agent_id=body.agent_id,
        title=body.title,
        description=body.description,
        status=body.status or "todo",
        sort_order=count,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = (
        db.query(models.Task)
        .options(joinedload(models.Task.comments))
        .filter_by(id=task_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, body: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if body.title is not None:
        task.title = body.title
    if body.description is not None:
        task.description = body.description
    if body.status is not None:
        task.status = body.status
    if body.sort_order is not None:
        task.sort_order = body.sort_order
    if body.agent_id is not None:
        task.agent_id = body.agent_id
    if body.summary is not None:
        task.summary = body.summary

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"success": True}


@router.post("/reorder")
def reorder_tasks(body: schemas.TaskReorder, db: Session = Depends(get_db)):
    for item in body.tasks:
        db.query(models.Task).filter_by(id=item.id).update(
            {"status": item.status, "sort_order": item.sort_order}
        )
    db.commit()
    return {"success": True}
