#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting CryptoTrader Pro...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if config.yaml exists
if [ ! -f "config/config.yaml" ]; then
    echo -e "${RED}Error: config.yaml not found${NC}"
    echo "Please run setup.py first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please run setup.py first"
    exit 1
fi

# Run the application
python src/main.py

# Deactivate virtual environment
deactivate 