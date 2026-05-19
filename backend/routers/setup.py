import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/setup", tags=["setup"])


def _get_config(db: Session) -> dict:
    rows = db.query(models.Config).all()
    return {r.key: r.value for r in rows}


def _set_config(db: Session, key: str, value: str):
    row = db.query(models.Config).filter_by(key=key).first()
    if row:
        row.value = value
    else:
        db.add(models.Config(key=key, value=value))


def _create_agent_files(folder_path: str, agent_name: str):
    """Create CLAUDE.md and SKILL.md for a new agent folder."""
    try:
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        claude_path = os.path.join(folder_path, "CLAUDE.md")
        skill_path = os.path.join(folder_path, "SKILL.md")
        if not os.path.exists(claude_path):
            Path(claude_path).write_text(
                f"# {agent_name}\n\nInstructions for {agent_name}.\n\n"
                "## Behaviour\n- Execute tasks directly without asking questions.\n"
                "- Add a comment summarising what was done after each action.\n",
                encoding="utf-8",
            )
        if not os.path.exists(skill_path):
            Path(skill_path).write_text(
                f"# Skills for {agent_name}\n\nList skills and tools available to {agent_name}.\n",
                encoding="utf-8",
            )
    except OSError:
        pass  # Path may not be writable in dev / different OS


@router.get("", response_model=schemas.SetupOut)
def get_setup(db: Session = Depends(get_db)):
    cfg = _get_config(db)
    return schemas.SetupOut(
        isSetup=bool(cfg.get("user_name")),
        user_name=cfg.get("user_name"),
        project_name=cfg.get("project_name"),
        folder_path=cfg.get("folder_path"),
    )


@router.post("", response_model=dict)
def post_setup(body: schemas.SetupIn, db: Session = Depends(get_db)):
    _set_config(db, "user_name", body.user_name)
    _set_config(db, "project_name", body.project_name)
    _set_config(db, "folder_path", body.folder_path)

    # Create base folder
    try:
        Path(body.folder_path).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    # Create default agent if none exists
    existing = db.query(models.Agent).filter_by(is_default=True).first()
    if not existing:
        agent_folder = os.path.join(body.folder_path, body.user_name)
        _create_agent_files(agent_folder, body.user_name)
        agent = models.Agent(
            name=body.user_name,
            folder_path=agent_folder,
            sort_order=0,
            is_default=True,
        )
        db.add(agent)

    db.commit()

    agents = db.query(models.Agent).all()
    return {"success": True, "agents": [schemas.AgentOut.model_validate(a).model_dump() for a in agents]}
