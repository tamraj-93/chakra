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
echo -e "${BLUE}     STARTING CHAKRA BACKEND SERVER (OPTIMIZED)   ${NC}"
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

# Performance settings
UVICORN_WORKERS=4
EOL
    echo -e "${GREEN}✓ Created .env file${NC}"
fi

# Determine the number of workers based on CPU cores
NUM_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
NUM_WORKERS=$(($NUM_CORES * 2 + 1))
echo -e "${GREEN}Detected ${NUM_CORES} CPU cores, using ${NUM_WORKERS} workers${NC}"

# Move to backend directory
cd backend || exit

# Check if Ollama is running
echo -e "${YELLOW}Checking Ollama status...${NC}"
if ! curl -s --head http://localhost:11434/api/version > /dev/null; then
    echo -e "${RED}Warning: Ollama service doesn't appear to be running${NC}"
    echo -e "${YELLOW}Make sure Ollama is running on http://localhost:11434${NC}"
    echo -e "${YELLOW}You can start Ollama with 'ollama serve' in another terminal${NC}"
    sleep 2
else
    echo -e "${GREEN}✓ Ollama is running${NC}"
    
    # Pre-warm the Ollama model
    echo -e "${YELLOW}Pre-warming the Ollama model...${NC}"
    MODEL_NAME=$(grep "OLLAMA_MODEL" .env | cut -d '=' -f2 || echo "mistral")
    curl -s -X POST http://localhost:11434/api/generate -d "{\"model\":\"$MODEL_NAME\",\"prompt\":\"Hello\",\"stream\":false}" > /dev/null
    echo -e "${GREEN}✓ Model pre-warmed${NC}"
fi

# Install required packages directly
echo -e "${YELLOW}Installing required packages...${NC}"
$PYTHON_CMD -m pip install -r requirements.txt || {
    echo -e "${YELLOW}Trying with user installation...${NC}"
    $PYTHON_CMD -m pip install --user -r requirements.txt
}

# Check for virtual environment
if [ -d "./venv" ]; then
    echo -e "${GREEN}Using virtual environment at ./venv${NC}"
    source ./venv/bin/activate
elif [ -d "./.venv" ]; then
    echo -e "${GREEN}Using virtual environment at ./.venv${NC}"
    source ./.venv/bin/activate
else
    echo -e "${YELLOW}No virtual environment found. Creating one...${NC}"
    $PYTHON_CMD -m venv ./.venv
    source ./.venv/bin/activate
    echo -e "${GREEN}Virtual environment created at ./.venv${NC}"
    echo -e "${YELLOW}Installing required packages in virtual environment...${NC}"
    pip install -r requirements.txt
fi

# Initialize healthcare templates
echo -e "${YELLOW}Initializing healthcare templates...${NC}"
python ./scripts/init_healthcare_templates.py

# Start the backend with optimized settings
echo -e "${YELLOW}Starting backend server with optimized settings...${NC}"

# In production mode, we don't use --reload flag
if [ "$1" == "--production" ]; then
    echo -e "${GREEN}Running in PRODUCTION mode (no auto-reload)${NC}"
    python -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers $NUM_WORKERS \
        --limit-concurrency 50 \
        --timeout-keep-alive 120 \
        --log-level warning
else
    echo -e "${YELLOW}Running in DEVELOPMENT mode (with auto-reload)${NC}"
    python -m uvicorn app.main:app \
        --reload \
        --host 0.0.0.0 \
        --port 8000 \
        --log-level info
fi

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     BACKEND SERVER STARTED                      ${NC}"
echo -e "${BLUE}     API available at: http://localhost:8000     ${NC}"
echo -e "${BLUE}==================================================${NC}"