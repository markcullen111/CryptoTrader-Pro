@echo off
echo Starting CryptoTrader Pro...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

REM Check if config.yaml exists
if not exist "config\config.yaml" (
    echo Error: config.yaml not found
    echo Please run setup.py first
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo Error: .env file not found
    echo Please run setup.py first
    pause
    exit /b 1
)

REM Run the application
python src/main.py

REM Deactivate virtual environment
deactivate

pause 