#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     CHAKRA LOCAL LLM SETUP - OLLAMA           ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if Ollama is already installed
if command_exists ollama; then
    echo -e "${GREEN}✓ Ollama is already installed${NC}"
    OLLAMA_VERSION=$(ollama --version)
    echo -e "  Version: $OLLAMA_VERSION"
else
    echo -e "${YELLOW}Installing Ollama...${NC}"
    
    # Check the operating system
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux installation
        echo -e "Detected Linux system, installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS installation
        echo -e "Detected macOS, installing Ollama..."
        if command_exists brew; then
            brew install ollama
        else
            echo -e "${RED}Homebrew not found. Please install Ollama manually:${NC}"
            echo -e "Visit https://ollama.com/download"
            exit 1
        fi
    else
        echo -e "${RED}Unsupported operating system. Please install Ollama manually:${NC}"
        echo -e "Visit https://ollama.com/download"
        exit 1
    fi
    
    # Verify installation
    if command_exists ollama; then
        echo -e "${GREEN}✓ Ollama installed successfully${NC}"
    else
        echo -e "${RED}✗ Ollama installation failed${NC}"
        echo -e "Please install manually from https://ollama.com/download"
        exit 1
    fi
fi

# Start Ollama service
echo -e "\n${YELLOW}Starting Ollama service...${NC}"
if pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✓ Ollama service is already running${NC}"
else
    # Start Ollama in the background
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

# Pull the Mistral model
echo -e "\n${YELLOW}Checking for Mistral model...${NC}"
if ollama list | grep -q "mistral"; then
    echo -e "${GREEN}✓ Mistral model is already downloaded${NC}"
else
    echo -e "Downloading Mistral model (this may take a while)..."
    ollama pull mistral
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Mistral model downloaded successfully${NC}"
    else
        echo -e "${RED}✗ Failed to download Mistral model${NC}"
        echo -e "You can try again later with: ollama pull mistral"
    fi
fi

# Update .env file
echo -e "\n${YELLOW}Updating configuration...${NC}"
ENV_FILE="../.env"

# Check if .env exists, create if not
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

# Update LLM_PROVIDER setting
if grep -q "^LLM_PROVIDER=" "$ENV_FILE"; then
    # Replace existing setting
    sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' "$ENV_FILE"
else
    # Add new setting
    echo "LLM_PROVIDER=ollama" >> "$ENV_FILE"
fi

# Update OLLAMA settings
if ! grep -q "^OLLAMA_API_URL=" "$ENV_FILE"; then
    echo "OLLAMA_API_URL=http://localhost:11434" >> "$ENV_FILE"
fi

if ! grep -q "^OLLAMA_MODEL=" "$ENV_FILE"; then
    echo "OLLAMA_MODEL=mistral" >> "$ENV_FILE"
fi

echo -e "${GREEN}✓ Configuration updated${NC}"

# Success message
echo -e "\n${BLUE}=================================================${NC}"
echo -e "${GREEN}     LOCAL LLM SETUP COMPLETE                    ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "Ollama is now configured to run with Chakra SLM."
echo -e "You can now use the local LLM for your SLA consultations."
echo -e "\nTo test the Ollama integration:"
echo -e "1. Restart your backend server"
echo -e "2. Use the consultation chat to ask questions"
echo -e "\nTo switch back to OpenAI, set LLM_PROVIDER=openai in your .env file."
echo -e "${BLUE}=================================================${NC}"