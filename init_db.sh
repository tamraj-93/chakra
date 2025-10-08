#!/bin/bash

# Script to initialize the database and sample data for Chakra application

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}     CHAKRA DATABASE INITIALIZER    ${NC}"
echo -e "${BLUE}====================================${NC}"

# Set the base directory to the script's location
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR/backend"

# Check for Python (try both python and python3 commands)
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python is not installed. Please install Python 3.8 or newer.${NC}"
        exit 1
    else
        PYTHON_CMD="python3"
    fi
fi

# Check if virtual environment exists, if not create it
if [ ! -d ".venv" ]; then
    echo -e "\n${YELLOW}Creating Python virtual environment...${NC}"
    $PYTHON_CMD -m venv .venv
    source .venv/bin/activate
    echo -e "\n${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Run the all-in-one initialization script
echo -e "\n${YELLOW}Running comprehensive database initialization...${NC}"
./scripts/init_all.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}Database initialization failed! Please check the error above.${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ Database initialization complete with template support!${NC}"
echo -e "\n${YELLOW}The database now includes:${NC}"
echo -e "  ${GREEN}✓${NC} User accounts"
echo -e "  ${GREEN}✓${NC} Sample consultations"
echo -e "  ${GREEN}✓${NC} SLA templates"
echo -e "  ${GREEN}✓${NC} Consultation templates"
echo -e "\n${YELLOW}You can now start the application with:${NC}"
echo -e "${GREEN}./start_chakra.sh${NC}"
echo -e "\n${YELLOW}====================================${NC}"