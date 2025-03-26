@echo off
setlocal enabledelayedexpansion

:: Colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

:: Check if virtual environment exists
if not exist "venv" (
    echo %RED%Virtual environment not found. Please run setup_windows.bat first.%NC%
    pause
    exit /b 1
)

:: Activate virtual environment
echo %YELLOW%Activating virtual environment...%NC%
call venv\Scripts\activate.bat

:: Check if required files exist
if not exist "config\config.yaml" (
    echo %RED%Configuration file not found. Please run setup_windows.bat first.%NC%
    pause
    exit /b 1
)

if not exist ".env" (
    echo %RED%Environment file not found. Please run setup_windows.bat first.%NC%
    pause
    exit /b 1
)

:: Start the application
echo %GREEN%Starting CryptoTrader Pro...%NC%
streamlit run app/streamlit_app/main.py 