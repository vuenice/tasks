"""
Task Manager — Python/FastAPI backend.

Start with:
    uvicorn main:app --reload --port 3333
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Ensure the database directory exists before importing models
Path("database").mkdir(exist_ok=True)

from database import Base, engine
import models  # noqa: F401 — registers ORM classes with Base

from routers import setup, agents, tasks, comments, routines

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan: create tables + start scheduler ──────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables (idempotent)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready")

    # Start the background scheduler and load active routines
    from services.scheduler import start as start_scheduler, stop as stop_scheduler
    start_scheduler()
    logger.info("Scheduler started")

    yield  # ← app is running

    # Shutdown
    stop_scheduler()
    logger.info("Scheduler stopped")


# ── FastAPI app ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Task Manager API",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server and any origin configured in .env
origins = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────

app.include_router(setup.router)
app.include_router(agents.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(routines.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
