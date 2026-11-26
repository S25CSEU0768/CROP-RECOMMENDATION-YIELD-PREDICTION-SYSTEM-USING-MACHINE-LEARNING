@echo off
title Stop Crop Recommendation ^& Yield Prediction System
color 0C

echo ======================================================================
echo           Stop Crop Recommendation ^& Yield Prediction System
echo               Bennett University - TEAM ROCKET (2025-2026)
echo ======================================================================
echo.
echo [*] Checking for active server instances on port 5000...

set FOUND=0
for /f "tokens=5" %%a in ('netstat -ano -p tcp ^| findstr /r /c:":5000 .*LISTENING"') do (
    echo [*] Terminating server process PID: %%a ...
    taskkill /F /PID %%a >nul 2>&1
    set FOUND=1
)

if "%FOUND%"=="1" (
    echo.
    echo [OK] Crop Recommendation ^& Yield Prediction System server stopped successfully.
) else (
    echo.
    echo [*] No running server found on port 5000.
)

echo.
ping 127.0.0.1 -n 2 >nul
exit /b
