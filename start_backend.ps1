#!/usr/bin/env pwsh
$backendDir = "J:\eithiroli\inter complletion folder\enterprise-lms abi~\backend"
$pythonExe = "J:\eithiroli\inter complletion folder\enterprise-lms abi~\backend\.venv\Scripts\python.exe"
& $pythonExe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000