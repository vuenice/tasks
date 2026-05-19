"""
Routines router — CRUD + manual trigger.

Routines are persisted in the DB and registered with APScheduler on the fly.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/routines", tags=["routines"])


def _get_scheduler():
    from services.scheduler import scheduler
    return scheduler


@router.get("", response_model=List[schemas.RoutineOut])
def list_routines(agent_id: int = None, db: Session = Depends(get_db)):
    q = db.query(models.Routine).order_by(models.Routine.created_at)
    if agent_id is not None:
        q = q.filter_by(agent_id=agent_id)
    return q.all()


@router.post("", response_model=schemas.RoutineOut)
def create_routine(body: schemas.RoutineCreate, db: Session = Depends(get_db)):
    if not db.query(models.Agent).get(body.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")

    routine = models.Routine(
        agent_id=body.agent_id,
        label=body.label,
        schedule=body.schedule,
        description=body.description,
        is_active=body.is_active if body.is_active is not None else True,
    )
    db.add(routine)
    db.commit()
    db.refresh(routine)

    # Register with scheduler if active and has a schedule
    if routine.is_active and routine.schedule:
        from services.scheduler import register_routine
        register_routine(routine)

    return routine


@router.put("/{routine_id}", response_model=schemas.RoutineOut)
def update_routine(routine_id: int, body: schemas.RoutineUpdate, db: Session = Depends(get_db)):
    routine = db.query(models.Routine).get(routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    if body.label is not None:
        routine.label = body.label
    if body.schedule is not None:
        routine.schedule = body.schedule
    if body.description is not None:
        routine.description = body.description
    if body.is_active is not None:
        routine.is_active = body.is_active

    db.commit()
    db.refresh(routine)

    # Re-register (or remove) from scheduler
    from services.scheduler import register_routine, unregister_routine
    if routine.is_active and routine.schedule:
        register_routine(routine)
    else:
        unregister_routine(routine_id)

    return routine


@router.delete("/{routine_id}")
def delete_routine(routine_id: int, db: Session = Depends(get_db)):
    routine = db.query(models.Routine).get(routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    from services.scheduler import unregister_routine
    unregister_routine(routine_id)

    db.delete(routine)
    db.commit()
    return {"success": True}


@router.post("/{routine_id}/run")
def run_now(routine_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger a routine immediately."""
    routine = db.query(models.Routine).get(routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    from services.scheduler import execute_routine
    background_tasks.add_task(execute_routine, routine_id)

    return {"success": True, "message": f"Routine '{routine.label}' triggered"}
