@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Please run setup_windows.bat first.
    pause
    exit /b 1
)
echo Starting the offline assistant.
.venv\Scripts\python.exe -m emporio.cli chat --mode offline
pause
