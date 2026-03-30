@echo off

cd /d %~dp0

cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
cd ..

cd frontend
if not exist node_modules (
    call npm install
)
cd ..

start cmd /k "cd %~dp0backend && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"
start cmd /k "cd %~dp0frontend && npm run dev"

echo Started!
pause
