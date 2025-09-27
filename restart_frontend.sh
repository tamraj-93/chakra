#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     FRONTEND API TEST                           ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Restart the frontend to apply changes
echo -e "${YELLOW}Restarting frontend to apply changes...${NC}"
cd /home/nilabh/Projects/chakra/frontend
pkill -f "ng serve" || echo "No Angular process found to kill"
sleep 2

# Start Angular in the background
echo -e "${YELLOW}Starting Angular frontend...${NC}"
ng serve --port 4200 &
FRONTEND_PID=$!

# Wait for frontend to initialize
echo -e "${YELLOW}Waiting for frontend to start (10 seconds)...${NC}"
sleep 10

# Check if frontend is running
if curl -s http://localhost:4200 > /dev/null; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not running${NC}"
    exit 1
fi

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     FRONTEND RESTARTED                          ${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "Now you can test the consultation page:"
echo -e "1. Open http://localhost:4200 in your browser"
echo -e "2. Log in with admin@example.com / password"
echo -e "3. Navigate to the consultation page"
echo -e "4. Check the browser console for any errors"
echo -e "${BLUE}==================================================${NC}"

# Keep the script running so that the frontend stays up
echo -e "${YELLOW}Press CTRL+C to stop the frontend server${NC}"
wait $FRONTEND_PID