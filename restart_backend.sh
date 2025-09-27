#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     RESTARTING CHAKRA BACKEND SERVER            ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Change to the workspace directory
cd "$(dirname "$0")" || exit

# Kill any existing backend processes
echo -e "${YELLOW}Stopping any existing backend processes...${NC}"
pkill -f "uvicorn app.main:app" || echo "No server was running"

# Wait a moment to ensure processes are terminated
sleep 2

# Check if virtual environment exists
if [ -d "./backend/venv" ]; then
    VENV_PATH="./backend/venv"
elif [ -d "./backend/.venv" ]; then
    VENV_PATH="./backend/.venv"
else
    echo -e "${RED}Error: Virtual environment not found.${NC}"
    echo -e "${YELLOW}Trying with system Python instead.${NC}"
    cd backend || exit
    pip install -r requirements.txt
    echo -e "${YELLOW}Starting backend server with system Python...${NC}"
    python -m uvicorn app.main:app --reload --host 0.0.0.0 &
    echo -e "${GREEN}✓ Backend server started with system Python${NC}"
    BACKEND_PID=$!
    cd ..
    return
fi

echo -e "${GREEN}Virtual environment found at ${VENV_PATH}.${NC}"
# Activate virtual environment and start server
echo -e "${YELLOW}Starting backend server...${NC}"
cd backend || exit
source $VENV_PATH/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓ Backend server started${NC}"

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     SERVER RESTART COMPLETE                     ${NC}"
echo -e "${BLUE}     API available at: http://localhost:8000     ${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server when finished${NC}"

# Wait for the server to be ready
sleep 3

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Server is running and healthy${NC}"
else
    echo -e "${RED}✗ Server failed to start properly${NC}"
fi

# Keep the script running so the background process doesn't terminate
wait