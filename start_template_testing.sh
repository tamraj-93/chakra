#!/bin/bash

# Script to start both backend and frontend for template testing

echo "Starting Chakra with Template Testing enabled..."

# Check if the backend is already running
if pgrep -f "python app/main.py" > /dev/null; then
  echo "Backend already running, skipping startup."
else
  echo "Starting backend..."
  # Start backend in a new terminal or in background
  ./start_backend.sh &
  BACKEND_PID=$!
  sleep 3
fi

echo "Starting frontend..."
cd frontend
npm start

# Cleanup function for graceful exit
function cleanup() {
  echo "Shutting down services..."
  if [ -n "$BACKEND_PID" ]; then
    kill $BACKEND_PID
  fi
  exit 0
}

# Set up trap for clean shutdown
trap cleanup SIGINT SIGTERM

# Wait for frontend to exit
wait