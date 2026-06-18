@echo off
cd /d "%~dp0"

set "BUNDLED_PYTHON=C:\Users\Aishita\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if exist "%BUNDLED_PYTHON%" (
  "%BUNDLED_PYTHON%" server.py
  goto :end
)

where python >nul 2>nul
if not errorlevel 1 (
  python server.py
  goto :end
)

where py >nul 2>nul
if not errorlevel 1 (
  py -3 server.py
  goto :end
)

echo Python 3 is required to start the backend.
echo Install Python 3, then run this file again.
pause
exit /b 1

:end
pause
