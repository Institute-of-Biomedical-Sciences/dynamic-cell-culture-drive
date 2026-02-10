@echo off
set PROJECT_DIR=C:\path\to\dynamic-cell-culture-drive
set BACKEND_DIR=%PROJECT_DIR%\backend
set FRONTEND_DIR=%PROJECT_DIR%\frontend


REM Start Docker Desktop (no-op if already running)
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
REM Wait for Docker Engine to become available
echo Waiting for Docker Engine...
:waitfordocker
docker info >nul 2>&1
if errorlevel 1 (
    timeout /t 2 >nul
    goto waitfordocker
)

REM Start services
docker compose up -f docker-compose-win.yml -d

REM ==========================
REM Start Backend (PowerShell)
REM ==========================
start "Backend API" powershell -NoExit -ExecutionPolicy Bypass -Command "cd '%BACKEND_DIR%'; .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM ==========================
REM Start Frontend
REM ==========================
start "Frontend Server" cmd /k "cd /d %FRONTEND_DIR% && npm install && npm run dev"

REM Open browser
timeout /t 2 > nul
start http://localhost:5173
