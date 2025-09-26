#!/bin/bash
# Backend setup script

# Exit on error
set -e

echo "Setting up Chakra SLM AI Assistant Backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment
cd backend
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Database connection
DATABASE_URL=postgresql://postgres:postgres@localhost/chakra

# Authentication
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI APIs
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
EOF
    echo ".env file created. Please edit it with your actual API keys."
fi

# Start the server
echo "Setup complete!"
echo "Run 'cd backend && source venv/bin/activate && uvicorn app.main:app --reload' to start the server."

# Return to the project root
cd ..