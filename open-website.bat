@echo off
cd /d "%~dp0"

set "BUNDLED_PYTHON=C:\Users\Aishita\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "PYTHON_CMD="

if exist "%BUNDLED_PYTHON%" set "PYTHON_CMD=%BUNDLED_PYTHON%"
if "%PYTHON_CMD%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)
if "%PYTHON_CMD%"=="" (
  where py >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if "%PYTHON_CMD%"=="" (
  echo Python 3 is required to start the website backend.
  echo You can still open index.html directly for the offline storefront.
  pause
  exit /b 1
)

start "Threadhaus Backend" cmd /k "%PYTHON_CMD% server.py"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000/"
