@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Please run setup_windows.bat first.
    pause
    exit /b 1
)
echo Checkpoint 01: deterministic catalog tools. Interactive chat is not implemented yet.
.venv\Scripts\python.exe -m emporio.cli --help
pause
