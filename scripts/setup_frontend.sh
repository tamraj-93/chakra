#!/bin/bash
# Frontend setup script

# Exit on error
set -e

echo "Setting up Chakra SLM AI Assistant Frontend..."

# Install dependencies
echo "Installing dependencies..."
npm install

# Create environment file if it doesn't exist
if [ ! -f "src/environments/environment.ts" ]; then
    echo "Creating environment file..."
    mkdir -p src/environments
    cat > src/environments/environment.ts << EOF
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
};
EOF
fi

# Start the development server
echo "Setup complete!"
echo "Run 'npm start' to start the development server."