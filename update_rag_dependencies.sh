#!/bin/bash

# Color codes for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo -e "${BLUE}${BOLD}          UPDATE RAG DEPENDENCIES IN CHAKRA ENVIRONMENT          ${NC}"
echo -e "${BLUE}${BOLD}==================================================================${NC}"

# Ensure we're working from the project root
PROJECT_ROOT="/home/nilabh/Projects/chakra"
cd "$PROJECT_ROOT" || {
    echo -e "${RED}Error: Could not change to project directory: $PROJECT_ROOT${NC}"
    exit 1
}

echo -e "${GREEN}Working directory: $(pwd)${NC}"

# Check for virtual environment
VENV_PATH=""
if [ -d "backend/.venv" ]; then
    VENV_PATH="backend/.venv"
elif [ -d "backend/venv" ]; then
    VENV_PATH="backend/venv"
fi

if [ -n "$VENV_PATH" ]; then
    echo -e "${GREEN}Found virtual environment at $VENV_PATH${NC}"
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}Virtual environment activated${NC}"
else
    echo -e "${RED}No virtual environment found. Please run start_chakra.sh first.${NC}"
    exit 1
fi

# Navigate to backend directory
cd backend || exit 1
echo -e "${GREEN}Changed to backend directory$(NC)"

# Update packages
echo -e "${BLUE}Updating pip...${NC}"
pip install --upgrade pip

echo -e "${BLUE}Installing RAG dependencies from requirements.txt...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}${BOLD}Dependencies updated successfully!${NC}"
echo -e "${GREEN}You can now run the healthcare RAG tests with:${NC}"
echo -e "${BLUE}cd ${PROJECT_ROOT} && ./run_healthcare_rag_test.sh${NC}"
echo -e "${BLUE}==================================================================${NC}"

# Deactivate virtual environment
deactivate