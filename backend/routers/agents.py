import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/agents", tags=["agents"])


def _create_agent_files(folder_path: str, agent_name: str):
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
        pass


@router.get("", response_model=List[schemas.AgentOut])
def list_agents(db: Session = Depends(get_db)):
    return db.query(models.Agent).order_by(models.Agent.sort_order, models.Agent.created_at).all()


@router.post("", response_model=schemas.AgentOut)
def create_agent(body: schemas.AgentCreate, db: Session = Depends(get_db)):
    # Get base folder from config
    cfg_row = db.query(models.Config).filter_by(key="folder_path").first()
    base_folder = cfg_row.value if cfg_row else "."

    agent_folder = os.path.join(base_folder, body.name)
    _create_agent_files(agent_folder, body.name)

    count = db.query(models.Agent).count()
    agent = models.Agent(
        name=body.name,
        folder_path=agent_folder,
        sort_order=count,
        is_default=False,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("/{agent_id}", response_model=schemas.AgentOut)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=schemas.AgentOut)
def update_agent(agent_id: int, body: schemas.AgentUpdate, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if body.name is not None:
        agent.name = body.name
    if body.move_to_agent_id is not None:
        agent.move_to_agent_id = body.move_to_agent_id
    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"success": True}


@router.post("/reorder")
def reorder_agents(body: schemas.AgentReorder, db: Session = Depends(get_db)):
    for i, agent_id in enumerate(body.order):
        db.query(models.Agent).filter_by(id=agent_id).update({"sort_order": i})
    db.commit()
    return {"success": True}


# ── CLAUDE.md ──────────────────────────────────────────────────────────────────

@router.get("/{agent_id}/instructions", response_model=schemas.InstructionsOut)
def get_instructions(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    content = ""
    if agent.folder_path:
        path = os.path.join(agent.folder_path, "CLAUDE.md")
        try:
            content = Path(path).read_text(encoding="utf-8")
        except OSError:
            pass

    return schemas.InstructionsOut(content=content, moveToAgentId=agent.move_to_agent_id)


@router.put("/{agent_id}/instructions")
def update_instructions(agent_id: int, body: schemas.InstructionsIn, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if body.move_to_agent_id is not None:
        agent.move_to_agent_id = body.move_to_agent_id
        db.commit()

    if agent.folder_path and body.content is not None:
        try:
            Path(agent.folder_path).mkdir(parents=True, exist_ok=True)
            Path(os.path.join(agent.folder_path, "CLAUDE.md")).write_text(body.content, encoding="utf-8")
        except OSError:
            pass

    return {"success": True, "content": body.content, "moveToAgentId": agent.move_to_agent_id}


# ── SKILL.md ───────────────────────────────────────────────────────────────────

@router.get("/{agent_id}/skills", response_model=schemas.SkillsOut)
def get_skills(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    content = ""
    if agent.folder_path:
        path = os.path.join(agent.folder_path, "SKILL.md")
        try:
            content = Path(path).read_text(encoding="utf-8")
        except OSError:
            pass

    return schemas.SkillsOut(content=content)


@router.put("/{agent_id}/skills")
def update_skills(agent_id: int, body: schemas.SkillsIn, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent.folder_path and body.content is not None:
        try:
            Path(agent.folder_path).mkdir(parents=True, exist_ok=True)
            Path(os.path.join(agent.folder_path, "SKILL.md")).write_text(body.content, encoding="utf-8")
        except OSError:
            pass

    return {"success": True, "content": body.content}
