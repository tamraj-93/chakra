#!/bin/bash

# Script to start both frontend and backend servers for the Chakra application

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
echo "       CHAKRA SLM ASSISTANT STARTUP        "
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

# Start the backend server
echo "Starting FastAPI backend on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
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

# Start the Angular dev server
echo "Starting Angular frontend on http://localhost:4200"
ng serve --port 4200 &
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