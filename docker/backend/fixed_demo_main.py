from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(title="Chakra - SLM AI Assistant (Demo Mode)")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Chakra SLM AI Assistant API (Demo Mode)"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mode": "demo"}

@app.get("/version")
async def version():
    """Version endpoint"""
    return {"version": "1.0.0", "mode": "demo"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def catch_all(request: Request, path: str):
    """Catch-all route that returns a mock response for any API endpoint"""
    method = request.method
    logger.info(f"Demo mode caught request: {method} /{path}")
    
    # Handle auth endpoints
    if path == "auth/login" or path.startswith("auth/"):
        return JSONResponse(
            status_code=200,
            content={
                "access_token": "demo_mock_token",
                "token_type": "bearer",
                "user": {"id": 1, "email": "demo@example.com", "is_active": True}
            }
        )
    
    # Handle users endpoints
    if path == "users" or path.startswith("users/"):
        return JSONResponse(
            status_code=200,
            content={
                "users": [
                    {"id": 1, "email": "admin@example.com", "name": "Admin User", "is_active": True},
                    {"id": 2, "email": "demo@example.com", "name": "Demo User", "is_active": True}
                ]
            }
        )
    
    # Handle consultation endpoints
    if path == "consultation" or path.startswith("consultation/"):
        return JSONResponse(
            status_code=200,
            content={
                "id": 123,
                "title": "Demo Consultation",
                "description": "This is a demo consultation in mock mode",
                "created_at": "2025-10-11T07:00:00Z",
                "status": "completed"
            }
        )
    
    # Default mock response
    return JSONResponse(
        status_code=200,
        content={
            "message": "This is a demo mode response",
            "path": path,
            "method": method,
            "demo_mode": True
        }
    )

# Add a catch-all error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for demo mode"""
    logger.error(f"Error in demo mode: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "An error occurred in demo mode",
            "error": str(exc),
            "path": request.url.path,
            "demo_mode": True
        }
    )

logger.info("Demo mode API server initialized")