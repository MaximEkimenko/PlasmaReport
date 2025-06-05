@echo off
set BACKEND_PATH=%~dp0
set FRONTEND_PATH=%~dp0frontend
set VENV_PATH=%~dp0.venv\Scripts\activate.bat

if not exist "%BACKEND_PATH%" (
    echo ERR: wrong backend path: %BACKEND_PATH%
    pause
    exit /b
)

if not exist "%FRONTEND_PATH%" (
    echo ERR: wrong frontend path: %FRONTEND_PATH%
    pause
    exit /b
)

if not exist "%VENV_PATH%" (
    echo ERR: wrong env: %VENV_PATH%
    pause
    exit /b
)

start "PlasmaReport Backend" cmd /k "cd /d %BACKEND_PATH% && call %VENV_PATH% && uvicorn main:app --host 0.0.0.0 --port 8005"

REM waiting for backend to start up
timeout /t 10 /nobreak >nul

REM start frontend
start "PlasmaReport Frontend" cmd /k "cd /d %FRONTEND_PATH% && npm run dev0000"

echo Backend и Frontend запущены в отдельных окнах.
