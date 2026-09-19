@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo Ultimate Video Agent - Setup
echo ========================================

where py >nul 2>nul
if %errorlevel%==0 (
    set "PY=py"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python was not found. Install Python 3.11 or 3.12 and run this again.
        exit /b 1
    )
    set "PY=python"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python environment...
    %PY% -m venv .venv
    if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

echo Installing Python packages...
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo.
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo WARNING: FFmpeg is not on PATH.
    echo The agent needs ffmpeg and ffprobe to analyze and render video.
) else (
    echo FFmpeg detected.
)

where ffprobe >nul 2>nul
if errorlevel 1 (
    echo WARNING: ffprobe is not on PATH.
) else (
    echo ffprobe detected.
)

echo.
echo Setup complete.
echo Run start.bat to launch the Video Production Agent.
echo Ollama is optional but improves editorial reasoning.
echo Local AI video generation is optional; run start_video_generator.bat when configured.
pause
