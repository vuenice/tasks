@echo off
REM Install deps (first run only)
pip install -r requirements.txt

REM Start FastAPI on port 3333
uvicorn main:app --reload --port 3333
