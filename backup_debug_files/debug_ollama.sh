#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     OLLAMA CONNECTION TEST                      ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}Ollama is not installed.${NC}"
    echo -e "${YELLOW}Please run ./scripts/setup_ollama.sh first.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    OLLAMA_VERSION=$(ollama --version)
    echo -e "  Version: $OLLAMA_VERSION"
fi

# Check if Ollama server is running
echo -e "\n${YELLOW}Checking if Ollama server is running...${NC}"
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${RED}✗ Ollama server is not running${NC}"
    echo -e "${YELLOW}Starting Ollama server...${NC}"
    ollama serve &
    OLLAMA_PID=$!
    echo -e "${GREEN}✓ Ollama server started with PID: $OLLAMA_PID${NC}"
    # Wait for Ollama to initialize
    sleep 3
else
    echo -e "${GREEN}✓ Ollama server is already running${NC}"
fi

# Check if mistral model is available
echo -e "\n${YELLOW}Checking if mistral model is available...${NC}"
if ! ollama list | grep -q "mistral"; then
    echo -e "${RED}✗ Mistral model is not available${NC}"
    echo -e "${YELLOW}Please run ./scripts/setup_ollama.sh to download the model.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Mistral model is available${NC}"
fi

# Test Ollama API directly
echo -e "\n${YELLOW}Testing Ollama API directly...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{
      "model": "mistral",
      "prompt": "What is an SLA?",
      "stream": false
    }')

if [ -z "$RESPONSE" ]; then
    echo -e "${RED}✗ No response received from Ollama API${NC}"
    echo -e "${YELLOW}Check if the Ollama server is running correctly.${NC}"
    exit 1
elif [[ "$RESPONSE" == *"error"* ]]; then
    echo -e "${RED}✗ Error received from Ollama API:${NC}"
    echo "$RESPONSE" | grep -o '"error":"[^"]*"' | sed 's/"error":"//'
    exit 1
else
    echo -e "${GREEN}✓ Successfully received response from Ollama API${NC}"
    echo -e "${BLUE}Sample response:${NC}"
    echo "$RESPONSE" | grep -o '"response":"[^"]*' | sed 's/"response":"//' | cut -c 1-200
    echo -e "${BLUE}...(truncated)${NC}"
fi

# Check if backend can connect to Ollama
echo -e "\n${YELLOW}Testing backend connection to Ollama...${NC}"
echo -e "${BLUE}Verifying environment settings:${NC}"

ENV_FILE="/home/nilabh/Projects/chakra/backend/.env"
if [ -f "$ENV_FILE" ]; then
    echo -e "Checking .env file..."
    grep -q "^LLM_PROVIDER=ollama" "$ENV_FILE" && echo -e "${GREEN}✓ LLM_PROVIDER is set to ollama${NC}" || echo -e "${RED}✗ LLM_PROVIDER is not set to ollama${NC}"
    grep -q "^OLLAMA_API_URL=" "$ENV_FILE" && echo -e "${GREEN}✓ OLLAMA_API_URL is defined${NC}" || echo -e "${RED}✗ OLLAMA_API_URL is not defined${NC}"
    grep -q "^OLLAMA_MODEL=" "$ENV_FILE" && echo -e "${GREEN}✓ OLLAMA_MODEL is defined${NC}" || echo -e "${RED}✗ OLLAMA_MODEL is not defined${NC}"
else
    echo -e "${RED}✗ .env file not found${NC}"
fi

echo -e "\n${BLUE}=================================================${NC}"
echo -e "${GREEN}     OLLAMA CONNECTION TEST COMPLETE             ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "If all checks passed, your Ollama integration should be working."
echo -e "If you're still having issues with the integration, check:"
echo -e "1. Backend logs for detailed error messages"
echo -e "2. Firewall settings that might block connections to port 11434"
echo -e "3. Restart both the Ollama service and the backend server"
echo -e "${BLUE}=================================================${NC}"