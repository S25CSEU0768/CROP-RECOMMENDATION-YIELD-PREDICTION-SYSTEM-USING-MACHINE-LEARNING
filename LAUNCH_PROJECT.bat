@echo off
title Crop Recommendation ^& Yield Prediction System
color 0A

echo ======================================================================
echo           Crop Recommendation ^& Yield Prediction System
echo               Bennett University - TEAM ROCKET (2025-2026)
echo ======================================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [!] Dedicated virtual environment not detected.
    echo [*] Attempting to launch with system Python...
    python run.py
    if errorlevel 1 (
        echo.
        echo [!] Failed to start with system Python.
        echo [*] Setup instructions: python -m venv venv and pip install -r requirements.txt
        pause
    )
    exit /b
)

echo [*] Starting Self-Healing Execution Pipeline...
echo [*] Checking port availability and trained machine learning models...
echo.

"venv\Scripts\python.exe" run.py

if errorlevel 1 (
    echo.
    echo [!] Server exited with an error. Check logs above.
    pause
)
