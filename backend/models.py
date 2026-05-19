from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship
from database import Base


class Config(Base):
    __tablename__ = "configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    folder_path = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)
    is_default = Column(Boolean, default=False)
    move_to_agent_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    routines = relationship("Routine", back_populates="agent", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="todo")      # todo | in_progress | done
    summary = Column(Text, nullable=True)        # auto-generated from comments by Claude
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("Agent", back_populates="tasks")
    comments = relationship(
        "Comment", back_populates="task",
        cascade="all, delete-orphan",
        order_by="Comment.created_at",
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String, default="user")      # user | claude
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")


class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    label = Column(String, nullable=False)
    schedule = Column(String, nullable=True)     # cron expression, e.g. "0 9 * * *"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("Agent", back_populates="routines")
