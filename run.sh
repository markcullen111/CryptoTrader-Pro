#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Virtual environment not found. Please run setup_linux.sh first.${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if required files exist
if [ ! -f "config/config.yaml" ]; then
    echo -e "${RED}Configuration file not found. Please run setup_linux.sh first.${NC}"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo -e "${RED}Environment file not found. Please run setup_linux.sh first.${NC}"
    exit 1
fi

# Start the application
echo -e "${GREEN}Starting CryptoTrader Pro...${NC}"
streamlit run app/streamlit_app/main.py 