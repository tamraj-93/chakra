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
    template_id: str = None,
    healthcare_template_id: str = None,
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
    logger.info(f"Template ID: {template_id}")
    logger.info(f"Healthcare Template ID: {healthcare_template_id}")
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
            
                # Comprehensive Ollama connectivity diagnostics
            import httpx
            import socket
            import subprocess
            from urllib.parse import urlparse
            
            ollama_checks = []
            
            try:
                # 1. Check basic socket connectivity
                parsed_url = urlparse(OLLAMA_API_URL)
                host = parsed_url.hostname or "localhost"
                port = parsed_url.port or 11434
                
                logger.info(f"Testing socket connectivity to {host}:{port}")
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((host, port))
                    s.close()
                    ollama_checks.append("✓ Socket connection: SUCCESS")
                except Exception as socket_exc:
                    ollama_checks.append(f"✗ Socket connection: FAILED - {str(socket_exc)}")
                
                # 2. Check with curl
                logger.info(f"Testing curl to {OLLAMA_API_URL}/api/tags")
                try:
                    result = subprocess.run(f"curl -s -m 5 {OLLAMA_API_URL}/api/tags", 
                                          shell=True, capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout:
                        ollama_checks.append("✓ Curl request: SUCCESS")
                    else:
                        ollama_checks.append(f"✗ Curl request: FAILED - {result.stderr}")
                except Exception as curl_exc:
                    ollama_checks.append(f"✗ Curl execution: FAILED - {str(curl_exc)}")
                
                # 3. Check with httpx client
                logger.info("Testing direct connection to Ollama API...")
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(f"{OLLAMA_API_URL}/api/tags")
                        if response.status_code == 200:
                            ollama_checks.append("✓ HTTPX request: SUCCESS")
                            models = response.json().get("models", [])
                            logger.info(f"Available models: {[m.get('name') for m in models]}")
                            
                            # Check if the configured model exists
                            model_names = [m.get('name') for m in models if 'name' in m]
                            if OLLAMA_MODEL in model_names or f"{OLLAMA_MODEL}:latest" in model_names:
                                ollama_checks.append(f"✓ Model '{OLLAMA_MODEL}' found")
                            else:
                                ollama_checks.append(f"✗ Model '{OLLAMA_MODEL}' not found in available models: {model_names}")
                        else:
                            ollama_checks.append(f"✗ HTTPX request: FAILED - Status {response.status_code}")
                            logger.error(f"Response: {response.text}")
                except Exception as e:
                    ollama_checks.append(f"✗ HTTPX request: FAILED - {str(e)}")
            
            except Exception as diag_exc:
                logger.error(f"✗ Ollama diagnostics error: {str(diag_exc)}")
            
            # Log all the check results
            logger.info("OLLAMA CONNECTIVITY CHECKS:")
            for check in ollama_checks:
                logger.info(check)
            logger.info("=" * 50)
        
        # Process user message and get AI response
        logger.info("Calling ai_service.process_message...")
        
        # We'll use a retry mechanism for better reliability
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    logger.info(f"Retry attempt {retry_count} of {max_retries}...")
                
                # Check if we have a healthcare template ID
                if healthcare_template_id:
                    # Use the healthcare template ID instead of the regular template ID
                    logger.info(f"Using healthcare template ID: {healthcare_template_id}")
                    template_to_use = healthcare_template_id
                else:
                    template_to_use = template_id
                
                response = await ai_service.process_message(
                    message.content,
                    message.role,
                    session_id,
                    current_user.id if current_user else None,
                    db,
                    template_to_use
                )
                
                # Check if we got a valid response
                if response and isinstance(response, dict) and "message" in response:
                    logger.info(f"AI Service response received, length: {len(str(response))}")
                    logger.info(f"Response keys: {response.keys()}")
                    logger.info("="*50)
                    return response
                else:
                    logger.warning(f"Unexpected response format: {response}")
                    retry_count += 1
                    continue
                    
            except Exception as retry_exc:
                logger.error(f"Error in process_message (attempt {retry_count+1}): {str(retry_exc)}")
                retry_count += 1
                if retry_count > max_retries:
                    # All retries failed
                    logger.error(f"All {max_retries} retries failed")
                    return {
                        "message": "I'm having technical difficulties connecting to my knowledge base. Please try again later.",
                        "session_id": session_id or 0,
                        "error_details": str(retry_exc) if message.role == "admin" else "Connection error after multiple retries"
                    }
                
                # Wait before retry (exponential backoff)
                import asyncio
                wait_time = 1 * (2 ** (retry_count - 1))  # 1, 2, 4, 8... seconds
                logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
        
        # This should not be reached due to the return in the loop, but just in case:
        logger.error("Unexpected exit from retry loop")
        return {
            "message": "I experienced an unexpected error. Please try again.",
            "session_id": session_id or 0
        }
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

@router.get("/sessions/{session_id}/check-stage-completion", response_model=Dict[str, Any])
async def check_stage_completion(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Check if the current stage in a template consultation is complete.
    
    This endpoint analyzes the conversation to determine if all required
    information for the current stage has been collected.
    """
    # Verify the session belongs to the user
    session = db.query(db_models.ConsultationSession).filter(
        db_models.ConsultationSession.id == session_id,
        db_models.ConsultationSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        # Call AI service to check stage completion
        result = await ai_service.check_stage_completion(db, session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check stage completion: {str(e)}"
        )

@router.post("/sessions/{session_id}/force-next-stage", response_model=Dict[str, Any])
async def force_next_stage(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Force transition to the next stage in a template consultation.
    This endpoint can be used when automatic stage progression fails.
    """
    # Verify the session belongs to the user
    session = db.query(db_models.ConsultationSession).filter(
        db_models.ConsultationSession.id == session_id,
        db_models.ConsultationSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        # Call AI service to force stage transition
        result = ai_service.force_stage_transition(db, session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to advance stage: {str(e)}"
        )

@router.post("/sessions/{session_id}/extract-template", response_model=Dict[str, Any])
async def extract_template_from_session(
    session_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """
    Extract a reusable template from a completed consultation session.
    This uses AI to analyze the conversation pattern and structure.
    """
    # Verify the session exists and belongs to the user
    session = db.query(db_models.ConsultationSession).filter(
        db_models.ConsultationSession.id == session_id,
        db_models.ConsultationSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get all messages for the session
    messages = db.query(db_models.Message).filter(
        db_models.Message.session_id == session_id
    ).order_by(db_models.Message.created_at).all()
    
    if not messages:
        raise HTTPException(status_code=400, detail="Cannot extract template from empty consultation")
    
    try:
        # Use the AI service to analyze the conversation and extract a template structure
        # This will be implemented using the Mistri LLM to identify patterns
        template_structure = await ai_service.extract_template_from_conversation(
            session=session,
            messages=messages
        )
        
        return template_structure
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract template: {str(e)}"
        )