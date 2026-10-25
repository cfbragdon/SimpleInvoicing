@echo off
title Simple Invoicing - close this window to stop the app
cd /d "%~dp0"

set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%PY%" (
    echo Could not find the project's Python at:
    echo   %PY%
    echo Create it with:  python -m venv .venv
    echo Then run:        .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo Using Python: %PY%
start "" http://127.0.0.1:5880/
"%PY%" app.py
if errorlevel 1 pause
