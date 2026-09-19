@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo First-time setup is required.
    call setup.bat
    if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
python app.py
