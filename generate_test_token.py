#!/usr/bin/env python3
"""
Generate a test JWT token for the Chakra application.
"""

from datetime import datetime, timedelta
import jwt

# Use the same values from config.py
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Create a token that will last for 24 hours
token = create_access_token(
    data={"sub": "admin@example.com"},
    expires_delta=timedelta(hours=24)
)

print("Token for testing:")
print(token)