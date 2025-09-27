#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     OLLAMA CONNECTION TEST                      ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama -v 2>/dev/null || ollama version 2>/dev/null)
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    echo -e "  Version: $OLLAMA_VERSION"
else
    echo -e "${RED}✗ Ollama is not installed${NC}"
    echo "Please install Ollama from https://ollama.ai"
    exit 1
fi

# Check if Ollama server is running
echo -e "\nChecking if Ollama server is running..."
if curl -s http://localhost:11434/api/tags >/dev/null; then
    echo -e "${GREEN}✓ Ollama server is already running${NC}"
else
    echo -e "${YELLOW}! Ollama server is not running, starting it...${NC}"
    ollama serve &
    OLLAMA_PID=$!
    sleep 5
    
    # Check again if server started
    if curl -s http://localhost:11434/api/tags >/dev/null; then
        echo -e "${GREEN}✓ Ollama server started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start Ollama server${NC}"
        exit 1
    fi
fi

# Check if mistral model is available
echo -e "\nChecking if mistral model is available..."
if curl -s http://localhost:11434/api/tags | grep -q "mistral"; then
    echo -e "${GREEN}✓ Mistral model is available${NC}"
else
    echo -e "${YELLOW}! Mistral model is not available, pulling it...${NC}"
    ollama pull mistral
    echo -e "${GREEN}✓ Mistral model pulled successfully${NC}"
fi

# Test Ollama API directly
echo -e "\nTesting Ollama API directly..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate -d '{
    "model": "mistral",
    "prompt": "What is an SLA?",
    "stream": false
}')

if [[ "$TEST_RESPONSE" == *"response"* ]]; then
    echo -e "${GREEN}✓ Successfully received response from Ollama API${NC}"
    SAMPLE_RESPONSE=$(echo "$TEST_RESPONSE" | grep -o '"response":"[^"]*"' | sed 's/"response":"//;s/"$//')
    echo -e "Sample response:\n ${SAMPLE_RESPONSE:0:500}..."
else
    echo -e "${RED}✗ Failed to get response from Ollama API${NC}"
    echo -e "Response: $TEST_RESPONSE"
    exit 1
fi

# Test backend connection to Ollama
echo -e "\nTesting backend connection to Ollama..."
echo -e "Verifying environment settings:"
echo -e "Checking .env file..."
if [ -f "./backend/.env" ]; then
    if grep -q "^LLM_PROVIDER=ollama" "./backend/.env"; then
        echo -e "${GREEN}✓ LLM_PROVIDER is set to ollama${NC}"
    else
        echo -e "${RED}✗ LLM_PROVIDER is not set to ollama${NC}"
        echo -e "Updating .env file..."
        sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' "./backend/.env"
        echo -e "${GREEN}✓ Updated LLM_PROVIDER to ollama${NC}"
    fi
    
    if grep -q "^OLLAMA_API_URL=" "./backend/.env"; then
        echo -e "${GREEN}✓ OLLAMA_API_URL is defined${NC}"
    else
        echo -e "${RED}✗ OLLAMA_API_URL is not defined${NC}"
        echo -e "Adding OLLAMA_API_URL to .env file..."
        echo "OLLAMA_API_URL=http://localhost:11434" >> "./backend/.env"
        echo -e "${GREEN}✓ Added OLLAMA_API_URL${NC}"
    fi
    
    if grep -q "^OLLAMA_MODEL=" "./backend/.env"; then
        echo -e "${GREEN}✓ OLLAMA_MODEL is defined${NC}"
    else
        echo -e "${RED}✗ OLLAMA_MODEL is not defined${NC}"
        echo -e "Adding OLLAMA_MODEL to .env file..."
        echo "OLLAMA_MODEL=mistral" >> "./backend/.env"
        echo -e "${GREEN}✓ Added OLLAMA_MODEL${NC}"
    fi
else
    echo -e "${RED}✗ .env file not found${NC}"
    echo -e "Creating .env file with Ollama settings..."
    cat > "./backend/.env" << EOL
# LLM Provider
LLM_PROVIDER=ollama
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral
EOL
    echo -e "${GREEN}✓ Created .env file with Ollama settings${NC}"
fi

echo -e "\n${BLUE}==================================================${NC}"
echo -e "${BLUE}     OLLAMA CONNECTION TEST COMPLETE             ${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "If all checks passed, your Ollama integration should be working."
echo -e "If you're still having issues with the integration, check:"
echo -e "1. Backend logs for detailed error messages"
echo -e "2. Firewall settings that might block connections to port 11434"
echo -e "3. Restart both the Ollama service and the backend server"
echo -e "${BLUE}==================================================${NC}"