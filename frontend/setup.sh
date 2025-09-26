#!/bin/bash

echo "Setting up Chakra SLM AI Assistant Frontend..."

# Install dependencies
npm install --legacy-peer-deps @angular/core@17.2.0 \
  @angular/common@17.2.0 \
  @angular/platform-browser@17.2.0 \
  @angular/platform-browser-dynamic@17.2.0 \
  @angular/forms@17.2.0 \
  @angular/router@17.2.0 \
  @angular/compiler@17.2.0 \
  rxjs@7.8.1 \
  zone.js@0.14.4 \
  tslib@2.6.2

# For development
npm install --save-dev --legacy-peer-deps @angular/cli@17.2.0 \
  @angular/compiler-cli@17.2.0 \
  typescript@5.3.3

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

echo "Frontend setup complete!"
echo "Run 'npm start' to start the development server."