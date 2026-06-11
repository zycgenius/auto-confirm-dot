@echo off
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.6+
    pause
    exit /b 1
)
start "" pythonw "%~dp0settings.py"
