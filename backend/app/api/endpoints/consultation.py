from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.models import consultation as consultation_models
from app.models import database as db_models
from app.services import ai as ai_service
from app.api.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/consultation",
    tags=["consultation"],
    responses={404: {"description": "Not found"}},
)

@router.post("/chat", response_model=Dict[str, Any])
async def chat_message(
    message: consultation_models.MessageBase, 
    session_id: int = None, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    import logging
    logger = logging.getLogger(__name__)
    
    # Enhanced debugging for consultation endpoint
    logger.info("="*50)
    logger.info(f"CONSULTATION CHAT API CALLED")
    logger.info(f"Message content: '{message.content}'")
    logger.info(f"Message role: '{message.role}'")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"User ID: {current_user.id if current_user else 'None'}")
    logger.info("="*50)
    
    try:
        # Enhanced environment debugging
        import os, sys
        logger.info("="*50)
        logger.info("ENVIRONMENT DIAGNOSTICS")
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"Current Directory: {os.getcwd()}")
        logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
        
        # Log LLM configuration
        from app.core.config import LLM_PROVIDER, OLLAMA_API_URL, OLLAMA_MODEL
        logger.info(f"Current LLM Provider: {LLM_PROVIDER}")
        if LLM_PROVIDER and LLM_PROVIDER.lower() == "ollama":
            logger.info(f"Ollama API URL: {OLLAMA_API_URL}")
            logger.info(f"Ollama Model: {OLLAMA_MODEL}")
            
            # Test direct connection to Ollama
            import httpx
            try:
                logger.info("Testing direct connection to Ollama API...")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{OLLAMA_API_URL}/api/tags")
                    if response.status_code == 200:
                        logger.info(f"✓ Ollama API connection successful: {response.status_code}")
                        models = response.json().get("models", [])
                        logger.info(f"Available models: {[m.get('name') for m in models]}")
                    else:
                        logger.error(f"✗ Ollama API connection failed: {response.status_code}")
                        logger.error(f"Response: {response.text}")
            except Exception as e:
                logger.error(f"✗ Ollama connection test error: {str(e)}")
        
        # Process user message and get AI response
        logger.info("Calling ai_service.process_message...")
        response = await ai_service.process_message(
            message.content,
            message.role,
            session_id,
            current_user.id if current_user else None,
            db
        )
        logger.info(f"AI Service response received, length: {len(str(response))}")
        logger.info(f"Response keys: {response.keys()}")
        logger.info("="*50)
        return response
    except Exception as e:
        logger.error("="*50)
        logger.error(f"ERROR PROCESSING CHAT: {str(e)}")
        logger.error("="*50, exc_info=True)
        # Return a more detailed error message for debugging
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Detailed traceback: {error_details}")
        
        return {
            "message": "I'm having trouble processing your request. Please try again later.", 
            "session_id": session_id or 0,
            "error_details": str(e) if message.role == "admin" else "Internal server error"
        }

@router.get("/sessions", response_model=List[consultation_models.ConsultationSession])
async def get_user_sessions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all consultation sessions for the current user"""
    # Query the database for the user's sessions
    sessions = db.query(db_models.ConsultationSession).filter(
        db_models.ConsultationSession.user_id == current_user.id
    ).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=consultation_models.ConsultationSession)
async def get_session(session_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get a specific consultation session with all messages"""
    # Query the database for the specific session, ensuring it belongs to the current user
    session = db.query(db_models.ConsultationSession).filter(
        db_models.ConsultationSession.id == session_id,
        db_models.ConsultationSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session