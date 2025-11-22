@echo off
REM Thai Portfolio Analyzer - Windows Startup Script

echo ========================================
echo Thai Portfolio Analyzer
echo ========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env and add your TYPHOON_API_KEY
    echo Get your API key from: https://opentyphoon.ai
    echo.
    pause
)

echo Configuration loaded
echo.

REM Check Python
python --version
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ========================================
echo Starting Thai Portfolio Analyzer...
echo ========================================
echo.
echo Access the application at:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python main.py

pause
