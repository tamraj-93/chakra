#!/bin/bash

# Master script to initialize, verify, and start the Chakra application

# Set colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Display header
echo -e "${BLUE}${BOLD}==========================================${NC}"
echo -e "${BLUE}${BOLD}      CHAKRA COMPLETE SETUP WIZARD       ${NC}"
echo -e "${BLUE}${BOLD}==========================================${NC}"

# Function to handle errors
handle_error() {
    echo -e "\n${RED}Error: $1${NC}"
    echo -e "${YELLOW}Setup aborted.${NC}"
    exit 1
}

# Step 1: Initialize the database
echo -e "\n${YELLOW}STEP 1: Initializing database${NC}"
./init_db.sh
if [ $? -ne 0 ]; then
    handle_error "Database initialization failed"
fi

# Step 2: Verify the database
echo -e "\n${YELLOW}STEP 2: Verifying database${NC}"
./verify_db.sh
if [ $? -ne 0 ]; then
    handle_error "Database verification failed"
fi

# Step 3: Run the API test
echo -e "\n${YELLOW}STEP 3: Testing API connectivity${NC}"
# Check if the backend is already running
if nc -z localhost 8000 2>/dev/null; then
    echo -e "${GREEN}Backend is already running on port 8000${NC}"
else
    echo -e "${YELLOW}Starting backend server for testing...${NC}"
    # Start the backend in background
    cd backend
    source .venv/bin/activate
    echo -e "${YELLOW}Starting temporary backend server...${NC}"
    python3 -m uvicorn app.main:app --port 8000 &
    SERVER_PID=$!
    
    # Wait for the server to start
    echo -e "${YELLOW}Waiting for server to start...${NC}"
    sleep 5
    
    # Run the API test
    cd ..
    ./test_api.sh
    
    # Kill the temporary server
    kill $SERVER_PID
    echo -e "${YELLOW}Temporary server stopped${NC}"
fi

# Step 4: Start the application
echo -e "\n${YELLOW}STEP 4: Starting the application${NC}"
echo -e "${GREEN}All checks passed! Your application is ready to use.${NC}"
echo -e "${GREEN}To start the application, run: ./start_chakra.sh${NC}"

echo -e "\n${BLUE}${BOLD}==========================================${NC}"
echo -e "${GREEN}${BOLD}           SETUP COMPLETE!              ${NC}"
echo -e "${BLUE}${BOLD}==========================================${NC}"
echo -e "You can now run the application with: ${GREEN}./start_chakra.sh${NC}"