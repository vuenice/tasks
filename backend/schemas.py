from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ─── Config ───────────────────────────────────────────────────────────────────

class SetupIn(BaseModel):
    user_name: str
    project_name: str
    folder_path: str


class SetupOut(BaseModel):
    isSetup: bool
    user_name: Optional[str] = None
    project_name: Optional[str] = None
    folder_path: Optional[str] = None


# ─── Agent ────────────────────────────────────────────────────────────────────

class AgentOut(BaseModel):
    id: int
    name: str
    folder_path: Optional[str]
    sort_order: int
    is_default: bool
    move_to_agent_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentCreate(BaseModel):
    name: str


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    move_to_agent_id: Optional[int] = None


class AgentReorder(BaseModel):
    order: List[int]


class InstructionsOut(BaseModel):
    content: str
    moveToAgentId: Optional[int] = None


class InstructionsIn(BaseModel):
    content: str
    move_to_agent_id: Optional[int] = None


class SkillsOut(BaseModel):
    content: str


class SkillsIn(BaseModel):
    content: str


# ─── Comment ──────────────────────────────────────────────────────────────────

class CommentOut(BaseModel):
    id: int
    task_id: int
    content: str
    author: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str
    author: Optional[str] = "user"


# ─── Task ─────────────────────────────────────────────────────────────────────

class TaskOut(BaseModel):
    id: int
    agent_id: int
    title: str
    description: Optional[str]
    status: str
    summary: Optional[str]
    sort_order: int
    created_at: datetime
    updated_at: datetime
    comments: List[CommentOut] = []

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    agent_id: int
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None
    agent_id: Optional[int] = None
    summary: Optional[str] = None


class TaskReorderItem(BaseModel):
    id: int
    status: str
    sort_order: int


class TaskReorder(BaseModel):
    tasks: List[TaskReorderItem]


# ─── Routine ──────────────────────────────────────────────────────────────────

class RoutineOut(BaseModel):
    id: int
    agent_id: int
    label: str
    schedule: Optional[str]
    description: Optional[str]
    is_active: bool
    last_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoutineCreate(BaseModel):
    agent_id: int
    label: str
    schedule: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True


class RoutineUpdate(BaseModel):
    label: Optional[str] = None
    schedule: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
