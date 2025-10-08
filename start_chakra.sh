#!/bin/bash

# Optimized script to start both frontend and backend servers for the Chakra application

# Set the base directory to the script's location
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to handle CTRL+C (SIGINT)
function cleanup {
    echo -e "\n\nShutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set up trap to catch SIGINT (CTRL+C)
trap cleanup SIGINT

# Display header
echo "==========================================="
echo "   CHAKRA SLM ASSISTANT STARTUP (OPTIMIZED)"
echo "==========================================="

# Check for dependencies
echo "Checking dependencies..."

# Set Python command - assume python3 is available in a Linux environment
PYTHON_CMD="python3"
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or newer."
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js 14.x or newer."
    exit 1
fi

# Check for Angular CLI
if ! command -v ng &> /dev/null; then
    echo "Angular CLI is not installed. Please install it with: npm install -g @angular/cli"
    exit 1
fi

# Check if running in production mode
PRODUCTION_MODE=false
if [ "$1" == "--production" ]; then
    PRODUCTION_MODE=true
    echo "Running in PRODUCTION mode"
else
    echo "Running in DEVELOPMENT mode"
fi

# Determine the number of workers based on CPU cores
NUM_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
NUM_WORKERS=$(($NUM_CORES * 2 + 1))
echo "Detected ${NUM_CORES} CPU cores, using ${NUM_WORKERS} workers for backend"

# Check Ollama status and pre-warm model
echo "Checking Ollama status..."
if ! curl -s --head http://localhost:11434/api/version > /dev/null; then
    echo "Warning: Ollama service doesn't appear to be running"
    echo "Make sure Ollama is running on http://localhost:11434"
    echo "You can start Ollama with 'ollama serve' in another terminal"
    sleep 2
else
    echo "✓ Ollama is running"
    
    # Read model name from .env file or use default
    MODEL_NAME="mistral"
    if [ -f "$BASE_DIR/backend/.env" ]; then
        MODEL_NAME=$(grep "OLLAMA_MODEL" $BASE_DIR/backend/.env | cut -d '=' -f2 || echo "mistral")
    fi
    
    # Pre-warm the Ollama model
    echo "Pre-warming the Ollama model (${MODEL_NAME})..."
    curl -s -X POST http://localhost:11434/api/generate -d "{\"model\":\"$MODEL_NAME\",\"prompt\":\"Hello\",\"stream\":false}" > /dev/null
    echo "✓ Model pre-warmed"
fi

# Start Backend
echo -e "\n\nStarting backend server..."
cd "$BASE_DIR/backend"

# Check if virtual environment exists, if not create it
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv .venv
    source .venv/bin/activate
    # Use python's built-in pip to avoid path issues
    $PYTHON_CMD -m pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Initialize healthcare templates
echo "Initializing healthcare templates..."
$PYTHON_CMD ./scripts/init_healthcare_templates.py
echo "✓ Healthcare templates initialized"

# Start the backend server with optimized settings
echo "Starting FastAPI backend on http://localhost:8000"
if [ "$PRODUCTION_MODE" = true ]; then
    uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers $NUM_WORKERS \
        --limit-concurrency 50 \
        --timeout-keep-alive 120 \
        --log-level warning &
else
    uvicorn app.main:app \
        --reload \
        --host 0.0.0.0 \
        --port 8000 \
        --log-level info &
fi

BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Wait a moment for the backend to initialize
sleep 2

# Start Frontend
echo -e "\n\nStarting frontend server..."
cd "$BASE_DIR/frontend"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start the Angular dev server with optimizations
echo "Starting Angular frontend on http://localhost:4200"
if [ "$PRODUCTION_MODE" = true ]; then
    # Use production configuration
    ng serve --port 4200 --prod --aot &
else
    ng serve --port 4200 &
fi

FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

echo -e "\n\n==========================================="
echo "All services started successfully!"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:4200"
echo "- API Docs: http://localhost:8000/docs"
echo "==========================================="
echo "Press CTRL+C to shut down all servers"
echo "==========================================="

# Wait for both processes to finish (or until CTRL+C)
wait