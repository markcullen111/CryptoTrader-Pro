@echo off
setlocal enabledelayedexpansion

:: Colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

echo %GREEN%Starting CryptoTrader Pro Setup...%NC%

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Python is not installed. Please install Python 3.8 or later from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.%NC%
    pause
    exit /b 1
)

:: Create virtual environment
echo %YELLOW%Creating virtual environment...%NC%
python -m venv venv

:: Activate virtual environment
echo %YELLOW%Activating virtual environment...%NC%
call venv\Scripts\activate.bat

:: Upgrade pip
echo %YELLOW%Upgrading pip...%NC%
python -m pip install --upgrade pip

:: Install dependencies
echo %YELLOW%Installing dependencies...%NC%
pip install -r requirements.txt

:: Create necessary directories
echo %YELLOW%Creating necessary directories...%NC%
mkdir logs 2>nul
mkdir data 2>nul
mkdir models 2>nul
mkdir config 2>nul

:: Create default configuration if it doesn't exist
if not exist "config\config.yaml" (
    echo %YELLOW%Creating default configuration...%NC%
    (
        echo exchange:
        echo   name: binance
        echo   api_key: ""
        echo   api_secret: ""
        echo   testnet: false
        echo.
        echo trading:
        echo   default_symbol: "BTC/USDT"
        echo   default_timeframe: "1h"
        echo   risk_per_trade: 0.02
        echo   max_positions: 5
        echo.
        echo risk_management:
        echo   max_drawdown: 0.1
        echo   stop_loss: 0.02
        echo   take_profit: 0.04
        echo   trailing_stop: 0.01
        echo.
        echo logging:
        echo   level: INFO
        echo   file: logs/app.log
        echo   max_size: 10485760  # 10MB
        echo   backup_count: 5
        echo.
        echo ui:
        echo   theme: dark
        echo   refresh_rate: 5
    ) > config\config.yaml
)

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo %YELLOW%Creating .env file...%NC%
    (
        echo EXCHANGE_API_KEY=your_api_key_here
        echo EXCHANGE_API_SECRET=your_api_secret_here
    ) > .env
)

echo %GREEN%Setup completed successfully!%NC%
echo %YELLOW%Please edit the following files with your configuration:%NC%
echo 1. config\config.yaml - Update your exchange settings
echo 2. .env - Add your API keys
echo.
echo %YELLOW%To start the application, run:%NC%
echo run.bat
pause 