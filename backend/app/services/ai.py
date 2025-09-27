from sqlalchemy.orm import Session
import os
import logging
from typing import Dict, Any, Optional

from app.models import database as db_models
from app.core.config import LLM_PROVIDER
from .llm_provider import LLMProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider

# Set up logging
logger = logging.getLogger(__name__)

def get_llm_provider() -> LLMProvider:
    """
    Factory function to get the configured LLM provider.
    
    Returns:
        LLMProvider: The configured LLM provider instance
    """
    provider_name = LLM_PROVIDER.lower() if LLM_PROVIDER else "openai"
    
    if provider_name == "ollama":
        logger.info("Using Ollama LLM provider")
        return OllamaProvider()
    else:
        logger.info("Using OpenAI LLM provider")
        return OpenAIProvider()

async def process_message(
    content: str,
    role: str,
    session_id: Optional[int],
    user_id: Optional[int],
    db: Session
) -> Dict[str, Any]:
    """Process a message and return an AI response."""
    
    # Get or create a new consultation session
    session = None
    if session_id:
        session = db.query(db_models.ConsultationSession).filter(
            db_models.ConsultationSession.id == session_id
        ).first()
    
    if not session:
        # Create a new session
        session = db_models.ConsultationSession(
            user_id=user_id,
            session_type="discovery",  # Default type
            context_data={},
            recommendations={}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Save the user message
    user_message = db_models.Message(
        session_id=session.id,
        content=content,
        role=role
    )
    db.add(user_message)
    db.commit()
    
    # Get previous messages in this session
    messages = db.query(db_models.Message).filter(
        db_models.Message.session_id == session.id
    ).order_by(db_models.Message.timestamp).all()
    
    # Format messages for OpenAI API
    openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    # Add system message if not present
    if not any(msg.role == "system" for msg in messages):
        system_message = {
            "role": "system", 
            "content": "You are an AI assistant specializing in Service Level Management (SLM). "
                      "You help users create and optimize Service Level Agreements (SLAs). "
                      "Ask clarifying questions to understand their needs and provide tailored advice."
        }
        openai_messages.insert(0, system_message)
    
    # Get AI response
    response = await get_ai_response(openai_messages)
    
    # Save AI response to database
    ai_message = db_models.Message(
        session_id=session.id,
        content=response,
        role="assistant"
    )
    db.add(ai_message)
    
    # Track token usage
    # This is simplified; real implementation would calculate actual token usage
    token_usage = db_models.TokenUsage(
        user_id=user_id,
        tokens_consumed=len(content) + len(response),  # Simplified estimation
        endpoint="chat",
        session_id=session.id
    )
    db.add(token_usage)
    db.commit()
    
    return {
        "message": response,
        "session_id": session.id
    }

async def get_ai_response(messages: list) -> str:
    """
    Get a response from the configured LLM provider.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        Generated text response as a string
    """
    try:
        # Get the configured provider
        provider = get_llm_provider()
        
        # Generate response using the provider
        return await provider.generate_response(
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
    except Exception as e:
        # Log the error and return a friendly message
        logger.error(f"Error getting AI response: {e}")
        return "I'm having trouble processing your request. Please try again later."