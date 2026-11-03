@echo off
setlocal
cd /d "%~dp0"
if not exist pyproject.toml (
    echo ERROR: Extract the entire ZIP before running this file.
    pause
    exit /b 1
)
python --version
if errorlevel 1 goto failed
if not exist .venv\Scripts\python.exe python -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -e .
if errorlevel 1 goto failed
if not exist .env copy .env.example .env >nul
echo.
echo Setup complete. No API key is required for Checkpoint 01.
echo Run start_windows.bat to view the available commands.
echo Run tests with: .venv\Scripts\python.exe -m unittest discover -s tests -v
pause
exit /b 0
:failed
echo Setup failed. Check the error above. Python 3.11 or later is required.
pause
exit /b 1
