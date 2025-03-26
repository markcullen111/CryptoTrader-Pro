#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting CryptoTrader Pro Setup...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Installing Python 3...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 is not installed. Installing pip3...${NC}"
    sudo apt-get install -y python3-pip
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p data
mkdir -p models
mkdir -p config

# Create default configuration if it doesn't exist
if [ ! -f "config/config.yaml" ]; then
    echo -e "${YELLOW}Creating default configuration...${NC}"
    cat > config/config.yaml << EOL
exchange:
  name: binance
  api_key: ""
  api_secret: ""
  testnet: false

trading:
  default_symbol: "BTC/USDT"
  default_timeframe: "1h"
  risk_per_trade: 0.02
  max_positions: 5

risk_management:
  max_drawdown: 0.1
  stop_loss: 0.02
  take_profit: 0.04
  trailing_stop: 0.01

logging:
  level: INFO
  file: logs/app.log
  max_size: 10485760  # 10MB
  backup_count: 5

ui:
  theme: dark
  refresh_rate: 5
EOL
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOL
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here
EOL
fi

# Make the run script executable
chmod +x run.sh

echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${YELLOW}Please edit the following files with your configuration:${NC}"
echo -e "1. config/config.yaml - Update your exchange settings"
echo -e "2. .env - Add your API keys"
echo -e "\nTo start the application, run:${NC}"
echo -e "./run.sh${NC}" 