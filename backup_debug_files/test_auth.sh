#!/bin/bash

# This script is used to verify that the authentication is working

# Check if the backend server is running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "Error: Backend server is not running at http://localhost:8000"
    echo "Please start the backend server first."
    exit 1
fi

# Test credentials
TEST_EMAIL="admin@example.com"
TEST_PASSWORD="password"

# Login and get token
echo "Attempting to login with test credentials..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

# Check if login failed
if [[ "$RESPONSE" == *"detail"* && "$RESPONSE" == *"Invalid"* ]]; then
    echo "Login failed. Response:"
    echo "$RESPONSE"
    echo ""
    echo "Try using these test credentials that should be in the database:"
    echo "Email: admin@example.com"
    echo "Password: admin123"
    exit 1
fi

# Extract token
TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\([^"]*\)"/\1/')

if [ -z "$TOKEN" ]; then
    echo "Failed to extract token from response:"
    echo "$RESPONSE"
    exit 1
fi

echo "Successfully logged in and retrieved token"
echo ""

# Test the consultation endpoint
echo "Testing consultation chat endpoint with token..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/consultation/chat \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"content\":\"Hello\",\"role\":\"user\"}")

echo "Chat endpoint response:"
echo "$CHAT_RESPONSE"
echo ""

if [[ "$CHAT_RESPONSE" == *"message"* ]]; then
    echo "✓ Authentication is working correctly!"
else
    echo "✗ Authentication test failed."
    echo "Response from endpoint did not contain expected data."
fi