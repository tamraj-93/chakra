#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     CHAKRA LLM INTEGRATION TEST                ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if the backend server is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${YELLOW}Backend server is not running. Starting it now...${NC}"
    
    # Kill any existing server
    pkill -f "uvicorn app.main:app" || echo "No server was running"
    sleep 2
    
    # Check for Python virtual environment
    if [ -d "./backend/venv" ]; then
        echo -e "${GREEN}Using virtual environment at ./backend/venv${NC}"
        VENV_DIR="./backend/venv"
    elif [ -d "./backend/.venv" ]; then
        echo -e "${GREEN}Using virtual environment at ./backend/.venv${NC}"
        VENV_DIR="./backend/.venv"
    else
        echo -e "${RED}No virtual environment found.${NC}"
        echo -e "${YELLOW}Please set up your Python environment first.${NC}"
        exit 1
    fi
    
    # Start backend server
    cd backend
    echo -e "${YELLOW}Starting backend server...${NC}"
    # Try to use system Python directly instead of venv
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../server.log 2>&1 &
    SERVER_PID=$!
    cd ..
    
    echo -e "${GREEN}Server started with PID $SERVER_PID${NC}"
    echo -e "${YELLOW}Waiting for server to initialize...${NC}"
    
    # Wait for server to start
    MAX_RETRIES=10
    RETRY_COUNT=0
    
    while ! curl -s http://localhost:8000/health > /dev/null; do
        RETRY_COUNT=$((RETRY_COUNT+1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo -e "${RED}Failed to start server after $MAX_RETRIES attempts${NC}"
            echo -e "${YELLOW}Check server.log for details${NC}"
            exit 1
        fi
        echo -e "${YELLOW}Waiting for server to start... (attempt $RETRY_COUNT/$MAX_RETRIES)${NC}"
        sleep 3
    done
    
    echo -e "${GREEN}✓ Server started successfully${NC}"
fi

# Test credentials
TEST_EMAIL="admin@example.com"
TEST_PASSWORD="password"

# Login and get token
echo -e "${YELLOW}Authenticating with test credentials...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

# Check if login failed
if [[ "$RESPONSE" == *"detail"* && "$RESPONSE" == *"Incorrect"* ]]; then
    echo -e "${RED}✗ Authentication failed${NC}"
    echo "$RESPONSE"
    echo -e "\nTry using these test credentials that should be in the database:"
    echo -e "Email: admin@example.com"
    echo -e "Password: password"
    exit 1
fi

# Extract token
TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\([^"]*\)"/\1/')

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Failed to extract token${NC}"
    echo "$RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Authentication successful${NC}"

# Test simple consultation query
echo -e "\n${YELLOW}Testing LLM integration with a simple query...${NC}"
QUERY="What is an SLA and why is it important?"

CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/consultation/chat \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"content\":\"$QUERY\",\"role\":\"user\"}")

echo -e "\n${GREEN}Query:${NC} $QUERY"
echo -e "\n${GREEN}Response:${NC}"
MESSAGE=$(echo $CHAT_RESPONSE | grep -o '"message":"[^"]*"' | sed 's/"message":"\([^"]*\)"/\1/')
echo -e "$MESSAGE"

# Check if the response contains the error message
if [[ "$MESSAGE" == "I'm having trouble processing your request. Please try again later." ]]; then
    echo -e "\n${RED}✗ LLM integration test failed${NC}"
    echo -e "The response indicates an error with the LLM provider."
    echo -e "Check your configuration and provider status."
else
    echo -e "\n${GREEN}✓ LLM integration test passed${NC}"
    echo -e "The LLM provider is responding correctly."
    
    # Check which provider is being used
    if grep -q "^LLM_PROVIDER=ollama" "../.env" 2>/dev/null; then
        echo -e "Using ${BLUE}Ollama${NC} local LLM provider"
    else
        echo -e "Using ${BLUE}OpenAI${NC} LLM provider"
    fi
fi

echo -e "\n${BLUE}=================================================${NC}"
echo -e "${BLUE}     TEST COMPLETE                               ${NC}"
echo -e "${BLUE}=================================================${NC}"