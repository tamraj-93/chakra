#!/bin/bash

# Helper script to get authentication token
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <username> <password>"
  exit 1
fi

USERNAME="$1"
PASSWORD="$2"

# Try to login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login   -H "Content-Type: application/json"   -d '{"username": "'$USERNAME'", "password": "'$PASSWORD'"}' | 
  grep -o '"access_token":"[^"]*' | 
  sed 's/"access_token":"//')

if [ -n "$TOKEN" ]; then
  echo "Authentication successful!"
  echo ""
  echo "Use this token in the debug tool:"
  echo "Bearer $TOKEN"
else
  echo "Authentication failed. Check your credentials."
fi
