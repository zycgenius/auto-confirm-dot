@echo off
python --version >nul 2>&1
if errorlevel 1 (
    echo 未检测到Python，请先安装Python 3.6+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
python "%~dp0auto_enter.py"
