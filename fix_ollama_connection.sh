#!/bin/bash

# Script to fix Ollama connectivity issues

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     CHAKRA OLLAMA CONNECTION FIX              ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if Ollama is running
if pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✓ Ollama service is running${NC}"
else
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    ollama serve &
    OLLAMA_PID=$!
    
    # Wait for Ollama to start
    echo -e "Waiting for Ollama service to start..."
    sleep 5
    
    if pgrep -x "ollama" > /dev/null; then
        echo -e "${GREEN}✓ Ollama service started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start Ollama service${NC}"
        exit 1
    fi
fi

# Verify the model exists
echo -e "\n${YELLOW}Checking for Mistral model...${NC}"
if ollama list | grep -q "mistral"; then
    echo -e "${GREEN}✓ Mistral model is available${NC}"
else
    echo -e "${YELLOW}Downloading Mistral model (this may take a while)...${NC}"
    ollama pull mistral
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Mistral model downloaded successfully${NC}"
    else
        echo -e "${RED}✗ Failed to download Mistral model${NC}"
        exit 1
    fi
fi

# Test direct connectivity
echo -e "\n${YELLOW}Testing direct connectivity to Ollama API...${NC}"
RESPONSE=$(curl -s -m 5 http://localhost:11434/api/tags)
if [ $? -eq 0 ] && [ ! -z "$RESPONSE" ]; then
    echo -e "${GREEN}✓ Direct connectivity to Ollama API works${NC}"
else
    echo -e "${RED}✗ Cannot connect to Ollama API${NC}"
    exit 1
fi

# Update the .env file
echo -e "\n${YELLOW}Updating .env configuration...${NC}"
ENV_FILE=".env"

# Create or update the .env file
cat > $ENV_FILE << EOL
LLM_PROVIDER=ollama
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Optional OpenAI settings (for fallback)
# OPENAI_API_KEY=
# OPENAI_MODEL=gpt-3.5-turbo
EOL

echo -e "${GREEN}✓ Updated .env file with Ollama configuration${NC}"

# Restart the backend
echo -e "\n${YELLOW}Restarting backend service...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null

# Check if Python virtual environment exists
if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✓ Found Python virtual environment${NC}"
    source backend/venv/bin/activate
else
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv backend/venv
    source backend/venv/bin/activate
    pip install -r backend/requirements.txt
fi

# Start the backend
cd backend
echo -e "${YELLOW}Starting backend with Ollama configuration...${NC}"
PYTHONUNBUFFERED=1 uvicorn app.main:app --reload > /tmp/chakra_backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✓ Backend started with PID: $BACKEND_PID${NC}"
echo -e "${GREEN}✓ Logs available at: /tmp/chakra_backend.log${NC}"
echo -e "\n${BLUE}=================================================${NC}"
echo -e "${BLUE}     CHAKRA OLLAMA CONNECTION FIXED           ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "\nBackend API is available at: http://localhost:8000"
echo -e "Press Ctrl+C to stop the server when finished"

# Wait for the background process
wait $BACKEND_PID