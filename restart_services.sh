#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}    Restarting Chakra Services      ${NC}"
echo -e "${BLUE}=====================================${NC}"

# Stop any running backend service
echo -e "\n${YELLOW}Stopping backend services...${NC}"
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    pkill -f "uvicorn app.main:app"
    echo -e "${GREEN}✓ Backend service stopped${NC}"
else
    echo -e "${YELLOW}No running backend service found${NC}"
fi

# Stop any running frontend service
echo -e "\n${YELLOW}Stopping frontend services...${NC}"
if pgrep -f "ng serve" > /dev/null; then
    pkill -f "ng serve"
    echo -e "${GREEN}✓ Frontend service stopped${NC}"
else
    echo -e "${YELLOW}No running frontend service found${NC}"
fi

# Start backend service
echo -e "\n${YELLOW}Starting backend service...${NC}"
cd backend
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}! Virtual environment not found, using system Python${NC}"
fi

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../server.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend service started with PID: $BACKEND_PID${NC}"

# Wait for backend to initialize
echo -e "${YELLOW}Waiting for backend to initialize...${NC}"
sleep 5

# Start frontend service
echo -e "\n${YELLOW}Starting frontend service...${NC}"
cd ../frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend service started with PID: $FRONTEND_PID${NC}"

echo -e "\n${GREEN}All services have been restarted!${NC}"
echo -e "${BLUE}------------------------------------${NC}"
echo -e "Backend running on: ${GREEN}http://localhost:8000${NC}"
echo -e "Frontend running on: ${GREEN}http://localhost:4200${NC}"
echo -e "${BLUE}------------------------------------${NC}"
echo -e "${YELLOW}Logs:${NC}"
echo -e "Backend log: ${BLUE}tail -f server.log${NC}"
echo -e "Frontend log: ${BLUE}tail -f frontend.log${NC}"