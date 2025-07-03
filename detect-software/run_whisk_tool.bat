@echo off
title Whisk Automation Tool - Professional Edition
echo.
echo ========================================
echo   Whisk Automation Tool - Professional
echo ========================================
echo.
echo Starting Whisk Automation Tool...
echo.

REM Try different Python commands
python whisk_gui.py 2>nul
if %errorlevel% neq 0 (
    py whisk_gui.py 2>nul
    if %errorlevel% neq 0 (
        python3 whisk_gui.py 2>nul
        if %errorlevel% neq 0 (
            echo.
            echo ERROR: Python not found!
            echo Please install Python from https://python.org
            echo.
            echo Support: Zalo 0379822057 (Nghia)
            echo.
            pause
            exit /b 1
        )
    )
)

echo.
echo Tool closed. Press any key to exit...
pause >nul
