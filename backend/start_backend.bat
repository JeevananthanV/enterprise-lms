@echo off
cd /d "J:\eithiroli\inter complletion folder\enterprise-lms abi~\backend"
call .venv\Scripts\activate
"J:\eithiroli\inter complletion folder\enterprise-lms abi~\backend\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000