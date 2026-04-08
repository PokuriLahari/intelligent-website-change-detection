@echo off
REM Website Monitor Startup Script for Windows

echo.
echo ========================================
echo   WatchDog - Website Monitor
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo.
    echo WARNING: .env file not found!
    echo.
    echo SETUP REQUIRED:
    echo 1. Copy .env.example to .env
    echo 2. Add your Gmail credentials to .env
    echo 3. Get App Password from: https://myaccount.google.com/apppasswords
    echo.
    pause
    exit /b 1
)

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Start the app
echo.
echo ✓ Dependencies installed
echo.
echo ========================================
echo   Starting WatchDog Monitor...
echo ========================================
echo.
echo.

python app.py

REM If app exits, show message
echo.
echo ========================================
echo   Server stopped. Press any key to exit...
echo ========================================
pause
