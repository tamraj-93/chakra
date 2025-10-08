#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to the script's directory
cd "$(dirname "$0")"

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     STARTING CHAKRA BACKEND SERVER              ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Kill any existing backend processes
echo -e "${YELLOW}Stopping any existing backend processes...${NC}"
pkill -f "uvicorn app.main:app" || echo "No server was running"

# Wait a moment to ensure processes are terminated
sleep 2

# Find Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}Using python3${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}Using python${NC}"
else
    echo -e "${RED}Error: Python is not installed${NC}"
    exit 1
fi

# Make sure .env file exists in backend directory
if [ ! -f "./backend/.env" ]; then
    echo -e "${YELLOW}Creating .env file with default settings...${NC}"
    cat > ./backend/.env << EOL
# Database connection
DATABASE_URL=sqlite:///chakra.db

# Authentication
SECRET_KEY=c3907fe25d74b6b7923e24d5090e2d5b73f71d5d3a51ff6197d4077f800f32a3
ACCESS_TOKEN_EXPIRE_MINUTES=60

# LLM Provider
LLM_PROVIDER=ollama
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral
EOL
    echo -e "${GREEN}✓ Created .env file${NC}"
fi

# Move to backend directory
cd backend || exit

# Install required packages directly
echo -e "${YELLOW}Installing required packages...${NC}"
$PYTHON_CMD -m pip install -r requirements.txt || {
    echo -e "${YELLOW}Trying with user installation...${NC}"
    $PYTHON_CMD -m pip install --user -r requirements.txt
}

# Check for virtual environment
if [ -d "./backend/venv" ]; then
    echo -e "${GREEN}Using virtual environment at ./backend/venv${NC}"
    source ./backend/venv/bin/activate
elif [ -d "./backend/.venv" ]; then
    echo -e "${GREEN}Using virtual environment at ./backend/.venv${NC}"
    source ./backend/.venv/bin/activate
else
    echo -e "${YELLOW}No virtual environment found. Creating one...${NC}"
    $PYTHON_CMD -m venv ./backend/venv
    source ./backend/venv/bin/activate
    echo -e "${GREEN}Virtual environment created at ./backend/venv${NC}"
    echo -e "${YELLOW}Installing required packages in virtual environment...${NC}"
    pip install -r ./backend/requirements.txt
fi

# Start the backend
echo -e "${YELLOW}Starting backend server...${NC}"
cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     BACKEND SERVER STARTED                      ${NC}"
echo -e "${BLUE}     API available at: http://localhost:8000     ${NC}"
echo -e "${BLUE}==================================================${NC}"