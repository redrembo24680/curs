@echo off
setlocal
set ROOT=%~dp0
cd /d "%ROOT%web_flask"

set "PYTHON=python"
if exist "%ROOT%venv\Scripts\python.exe" (
    set "PYTHON=%ROOT%venv\Scripts\python.exe"
)

%PYTHON% -m pip install -r requirements.txt >nul

set FLASK_APP=app.py
if not defined API_BASE_URL set API_BASE_URL=http://localhost:8080/api

%PYTHON% -m flask run --port 5000
endlocal