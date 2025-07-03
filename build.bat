@echo off
echo 🚀 Building Whisk Automation Tool...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python found

REM Install/upgrade required packages
echo.
echo 📦 Installing required packages...
pip install --upgrade pip
pip install -r requirements.txt

REM Run build script
echo.
echo 🔧 Running build script...
python build_exe.py

echo.
echo ✅ Build process completed!
pause
