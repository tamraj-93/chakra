"""
AI Service for Consultation Processing

This service handles AI-powered consultation functionality, including:
- Processing messages in consultation sessions
- Generating AI responses based on context and prompts
- Managing template-based consultations
- Extracting structured information from conversations
- Retrieval-Augmented Generation (RAG) for contextually-enhanced responses
"""
from sqlalchemy.orm import Session
import os
import logging
from typing import Dict, Any, Optional, List
import json

from app.models import database as db_models
from app.core.config import LLM_PROVIDER
from .llm_provider import LLMProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .prompts import get_industry_prompt
from .rag_service import get_rag_service

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

def detect_industry_from_message(content: str, current_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect industry mentions in a message and update the session context.
    
    Args:
        content: The message content to analyze
        current_context: The current session context data
        
    Returns:
        Updated context dictionary with industry information if detected
    """
    # Create a copy of the context to avoid modifying the original
    context = dict(current_context) if current_context else {}
    
    # List of industries and their keywords
    industries = {
        "healthcare": ["healthcare", "medical", "hospital", "patient", "doctor", "clinic", "health", "pharma"],
        "it_services": ["it", "software", "technology", "cloud", "computing", "tech", "digital", "server"],
        "financial_services": ["financial", "banking", "insurance", "bank", "finance", "investment", "loan"],
        "retail": ["retail", "store", "shop", "e-commerce", "customer", "product", "merchandise"],
        "manufacturing": ["manufacturing", "factory", "production", "assembly", "industrial"],
        "telecommunications": ["telecom", "telecommunication", "network", "cellular", "mobile"]
    }
    
    content_lower = content.lower()
    
    # Check for industry mentions in the message
    detected_industries = []
    for industry, keywords in industries.items():
        for keyword in keywords:
            if keyword in content_lower:
                detected_industries.append(industry)
                break
    
    # Update context if any industries were detected
    if detected_industries:
        if "industry" not in context or not context["industry"]:
            # Only use the first detected industry
            context["industry"] = detected_industries[0]
            logger.info(f"Detected industry: {detected_industries[0]}")
        
        # Store all detected industries for reference
        context["detected_industries"] = detected_industries
    
    return context


def create_consultation_session(
    db: Session,
    user_id: int,
    initial_message: str = None,
    template_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new consultation session for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        initial_message: Optional initial message from the user
        template_id: Optional template ID if this is a template-based consultation
        
    Returns:
        Dictionary with session information
    """
    try:
        # Determine session type based on whether a template is used
        session_type = "template" if template_id else "discovery"
        
        # Initialize session state if using a template
        session_state = None
        if template_id:
            session_state = {
                "template_id": template_id,
                "current_stage": None,  # Will be set to first stage below
                "completed_stages": [],
                "progress_percentage": 0,
                "extracted_data": {}
            }
        
        # Create the session in the database
        session = db_models.ConsultationSession(
            user_id=user_id,
            session_type=session_type,
            context_data={},
            recommendations={},
            template_id=template_id,
            session_state=session_state
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Created new {session_type} consultation session {session.id} for user {user_id}")
        
        # If this is a template-based consultation, set up the first stage
        if template_id:
            # Get the template data
            from app.models.database_templates import ConsultationTemplate
            
            template = db.query(ConsultationTemplate).filter(
                ConsultationTemplate.id == template_id
            ).first()
            
            if template and template.stages:
                # Set the first stage as current
                first_stage = template.stages[0]
                session.session_state["current_stage"] = first_stage.id
                db.commit()
                
                # Return session with first stage information
                return {
                    "session": session,
                    "session_id": session.id,
                    "current_stage": {
                        "id": first_stage.id,
                        "name": first_stage.name,
                        "description": first_stage.description,
                        "type": first_stage.stage_type
                    }
                }
        
        # For discovery sessions or if template setup fails
        return {
            "session": session,
            "session_id": session.id
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating consultation session: {str(e)}")
        raise


async def process_consultation_message(
    db: Session,
    session_id: int,
    message_content: str,
    user_id: int,
    stage_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a message in a consultation session and generate AI response.
    
    Args:
        db: Database session
        session_id: ID of the consultation session
        message_content: Message content from the user
        user_id: ID of the user
        stage_id: Optional stage ID for template-based consultations
        
    Returns:
        Dictionary with AI response and updated context
    """
    # Get the consultation session
    session = db.query(db_models.ConsultationSession).filter(
        db_models.ConsultationSession.id == session_id,
        db_models.ConsultationSession.user_id == user_id
    ).first()
    
    if not session:
        logger.error(f"Session {session_id} not found for user {user_id}")
        raise ValueError(f"Session {session_id} not found")
    
    # Get template data if this is a template-based session
    template_data = None
    current_stage = None
    
    if session.template_id:
        from app.models.database_templates import ConsultationTemplate, ExpectedOutput
        
        template = db.query(ConsultationTemplate).filter(
            ConsultationTemplate.id == session.template_id
        ).first()
        
        if template:
            # Format the template data for easier access
            template_data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "initial_system_prompt": template.initial_system_prompt,
                "stages": []
            }
            
            for stage in template.stages:
                # Convert expected outputs to dict format
                expected_outputs = []
                for output in stage.expected_outputs:
                    expected_outputs.append({
                        "name": output.name,
                        "description": output.description,
                        "data_type": output.data_type,
                        "required": output.required
                    })
                
                template_data["stages"].append({
                    "id": stage.id,
                    "name": stage.name,
                    "description": stage.description,
                    "stage_type": stage.stage_type,
                    "prompt_template": stage.prompt_template,
                    "system_instructions": stage.system_instructions,
                    "expected_outputs": expected_outputs,
                    "ui_components": stage.ui_components or {},
                    "next_stage_conditions": stage.next_stage_conditions or {},
                })
            
            # Get the current stage if we have one
            current_stage_id = session.session_state.get("current_stage") if session.session_state else None
            
            if current_stage_id:
                for stage in template_data["stages"]:
                    if stage["id"] == current_stage_id:
                        current_stage = stage
                        break
    
    # Get all previous messages in this session
    messages = db.query(db_models.Message).filter(
        db_models.Message.session_id == session_id
    ).order_by(db_models.Message.timestamp.asc()).all()
    
    # Convert messages to format expected by LLM provider
    message_history = []
    for msg in messages:
        message_history.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Add current message to history
    user_message = {
        "role": "user",
        "content": message_content
    }
    message_history.append(user_message)
    
    # Store the user message in the database
    db_user_message = db_models.Message(
        session_id=session_id,
        content=message_content,
        role="user",
        stage_id=stage_id or (current_stage["id"] if current_stage else None)
    )
    db.add(db_user_message)
    db.commit()
    
    # Update context based on message content
    context = detect_industry_from_message(message_content, session.context_data)
    
    # If there's updated context, save it
    if context != session.context_data:
        session.context_data = context
        db.commit()
    
    # Get appropriate system prompt
    system_prompt = ""
    
    if template_data and current_stage:
        # For template consultations, use the current stage's system instructions
        system_prompt = current_stage["system_instructions"]
        if current_stage["prompt_template"]:
            # Add the stage prompt template as the first assistant message
            message_history.insert(0, {
                "role": "assistant",
                "content": current_stage["prompt_template"]
            })
    else:
        # For discovery consultations, use industry-specific prompt if available
        industry = context.get("industry", "general")
        system_prompt = get_industry_prompt(industry)
    
    # Insert system prompt at the beginning
    if system_prompt:
        message_history.insert(0, {
            "role": "system",
            "content": system_prompt
        })
    
    # Get the LLM provider
    llm_provider = None
    if LLM_PROVIDER.lower() == "openai":
        llm_provider = OpenAIProvider()
    else:
        llm_provider = OllamaProvider()
    
    # Generate AI response
    try:
        ai_response_text = await llm_provider.generate_response(message_history)
        
        # Store the AI response in the database
        ai_message = db_models.Message(
            session_id=session_id,
            content=ai_response_text,
            role="assistant",
            stage_id=stage_id or (current_stage["id"] if current_stage else None)
        )
        db.add(ai_message)
        db.commit()
        
        # Check for stage completion if this is a template-based consultation
        stage_completed = False
        next_stage_info = None
        is_consultation_complete = False
        extracted_data = {}
        
        if template_data and current_stage:
            # Extract outputs from the AI response (would need advanced extraction logic)
            # For now, we're detecting stage completion based on message analysis
            latest_messages = [msg for msg in message_history[-10:] if msg["role"] in ["user", "assistant"]]
            
            # Check if the current stage is complete
            completion_status = detect_stage_completion(db, session_id, latest_messages, current_stage)
            stage_completed = completion_status["is_complete"]
            extracted_data = completion_status.get("extracted_data", {})
            
            # If stage is complete, update session state
            if stage_completed:
                # Find current stage index
                current_stage_index = -1
                for i, stage in enumerate(template_data["stages"]):
                    if stage["id"] == current_stage["id"]:
                        current_stage_index = i
                        break
                
                if current_stage_index >= 0 and current_stage_index + 1 < len(template_data["stages"]):
                    # There are more stages, advance to the next one
                    if session.session_state is None:
                        session.session_state = {}
                    
                    # Mark current stage as completed
                    completed_stages = session.session_state.get("completed_stages", [])
                    completed_stages.append(current_stage["id"])
                    
                    next_stage = template_data["stages"][current_stage_index + 1]
                    next_stage_info = {
                        "name": next_stage["name"],
                        "type": next_stage["stage_type"],
                        "description": next_stage["description"]
                    }
                    
                    # Update session state
                    session.session_state["current_stage"] = next_stage["id"]
                    session.session_state["completed_stages"] = completed_stages
                    progress = ((current_stage_index + 1) / len(template_data["stages"])) * 100
                    session.session_state["progress_percentage"] = progress
                    
                    # Add extracted data to session state
                    if "extracted_data" not in session.session_state:
                        session.session_state["extracted_data"] = {}
                    session.session_state["extracted_data"].update(extracted_data)
                    
                    db.commit()
                
                elif current_stage_index + 1 >= len(template_data["stages"]):
                    # This was the last stage, mark consultation as complete
                    completed_stages = session.session_state.get("completed_stages", [])
                    if current_stage["id"] not in completed_stages:
                        completed_stages.append(current_stage["id"])
                    
                    session.session_state["completed_stages"] = completed_stages
                    session.session_state["progress_percentage"] = 100
                    session.session_state["is_complete"] = True
                    
                    # Add extracted data to session state
                    if "extracted_data" not in session.session_state:
                        session.session_state["extracted_data"] = {}
                    session.session_state["extracted_data"].update(extracted_data)
                    
                    is_consultation_complete = True
                    db.commit()
        
        # Prepare response
        response = {
            "ai_response": ai_response_text,
            "updated_context": session.context_data,
        }
        
        if template_data and current_stage:
            response.update({
                "template_progress": {
                    "current_stage": current_stage["id"],
                    "stage_name": current_stage["name"],
                    "stage_type": current_stage["stage_type"],
                    "progress_percentage": session.session_state.get("progress_percentage", 0),
                    "stage_completed": stage_completed,
                    "is_complete": is_consultation_complete,
                }
            })
            
            if stage_completed and next_stage_info:
                response["template_progress"]["next_stage"] = next_stage_info
            
            if extracted_data:
                response["extracted_data"] = extracted_data
        
        return response
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing consultation message: {str(e)}")
        raise


async def detect_stage_completion(
    db: Session,
    session_id: int,
    recent_messages: List[Dict[str, str]],
    current_stage: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Intelligently detect if a stage in a template consultation is complete.
    
    This function analyzes conversation messages to determine if all required
    information for a stage has been collected, allowing for automatic
    progression to the next stage.
    
    Args:
        db: Database session
        session_id: ID of the consultation session
        recent_messages: List of recent messages in the conversation
        current_stage: Current stage data including expected outputs
        
    Returns:
        Dict with completion status and extracted data
    """
    logger.info(f"Analyzing stage completion for stage {current_stage['id']} in session {session_id}")
    
    # Check for debug/testing flag - force completion if set
    if os.getenv("DEBUG_FORCE_COMPLETION", "false").lower() == "true":
        logger.info("DEBUG_FORCE_COMPLETION is enabled, forcing stage completion")
        return {"is_complete": True, "confidence": 100, "extracted_data": {}, "reason": "DEBUG_FORCE_COMPLETION enabled"}
    
    # Get the session to determine template domain
    session = db.query(db_models.ConsultationSession).filter(
        db_models.ConsultationSession.id == session_id
    ).first()
    
    # Import here to avoid circular imports
    from app.models.database_templates import ConsultationTemplate
    
    # Get template domain if available
    template_domain = "general"
    if session and session.template_id:
        template = db.query(ConsultationTemplate).filter(
            ConsultationTemplate.id == session.template_id
        ).first()
        if template and template.domain:
            template_domain = template.domain.lower()
    
    # Special handling for health domain templates
    if "health" in template_domain or "medical" in template_domain or "symptom" in template_domain:
        logger.info(f"Using health domain completion rules for template domain: {template_domain}")
        
        # In health domain, check for health analysis indicators in AI responses
        if len(recent_messages) >= 2:  # At least one user message and one AI response
            # Find the most recent AI message
            ai_messages = [msg for msg in recent_messages if msg.get('role') == 'assistant']
            if ai_messages:
                last_ai_content = ai_messages[-1].get('content', '').lower()
                
                # Check for health assessment indicators
                health_indicators = [
                    "assessment", "diagnosis", "symptoms", "condition", 
                    "recommend", "analysis", "based on your", "medical history",
                    "health condition", "further tests", "treatment", "medication",
                    "health plan", "prognosis", "risk factors", "health record"
                ]
                
                if any(indicator in last_ai_content for indicator in health_indicators):
                    logger.info(f"Health domain stage completion detected with indicators in AI response")
                    return {"is_complete": True, "confidence": 95, "extracted_data": {}, 
                            "reason": "Health assessment indicators detected"}
    
    # Count user messages - if there are at least 3 messages, consider the stage complete
    # This is a fallback mechanism to ensure stages can progress
    user_messages = [msg for msg in recent_messages if msg.get('role') == 'user']
    if len(user_messages) >= 3:
        logger.info(f"Stage {current_stage['id']} marked complete based on message count ({len(user_messages)} messages)")
        return {"is_complete": True, "confidence": 85, "extracted_data": {}, "reason": "Sufficient messages provided"}
    
    # Extract expected outputs for this stage
    expected_outputs = current_stage.get("expected_outputs", [])
    
    # If no expected outputs, stage can't be evaluated for completion
    if not expected_outputs:
        logger.warning(f"No expected outputs defined for stage {current_stage['id']}")
        return {"is_complete": False, "confidence": 0, "extracted_data": {}}
    
    # Get the LLM provider
    llm_provider = get_llm_provider()
    
    # Format the expected outputs for the prompt
    formatted_outputs = []
    for output in expected_outputs:
        formatted_outputs.append(
            f"- {output['name']}: {output['description']} (Required: {output['required']}, Type: {output['data_type']})"
        )
    
    # Format recent messages for the prompt
    formatted_messages = []
    for msg in recent_messages:
        formatted_messages.append(f"{msg['role'].upper()}: {msg['content']}")
    
    # Create prompt for stage completion detection - simplified and more direct
    completion_prompt = f"""
    You are analyzing a consultation to determine if the current stage is complete.
    
    STAGE: {current_stage['name']}
    DESCRIPTION: {current_stage['description']}
    
    EXPECTED OUTPUTS:
    {formatted_outputs}
    
    RECENT CONVERSATION:
    {formatted_messages}
    
    HAS THE USER PROVIDED ALL REQUIRED INFORMATION FOR THIS STAGE?
    Answer with ONLY "YES" or "NO" first, then provide a brief explanation.
    """
    
    # Generate analysis
    try:
        analysis_response = await llm_provider.generate_response([
            {"role": "system", "content": "You are a specialized AI for analyzing conversation completeness."},
            {"role": "user", "content": completion_prompt}
        ])
        
        # Check for YES at the beginning of the response
        is_complete = "YES" in analysis_response[:10].upper()
        
        # Log the result
        if is_complete:
            logger.info(f"Stage {current_stage['id']} detected as complete")
            reason = analysis_response[10:100].strip() if len(analysis_response) > 10 else "Stage requirements met"
        else:
            logger.info(f"Stage {current_stage['id']} not complete")
            reason = analysis_response[10:100].strip() if len(analysis_response) > 10 else "Stage requirements not yet met"
        
        # Return simplified result
        return {
            "is_complete": is_complete, 
            "confidence": 90 if is_complete else 50,
            "reason": reason,
            "extracted_data": {}
        }
            
    except Exception as e:
        logger.error(f"Error detecting stage completion: {str(e)}")
        # If there's an error in LLM analysis, use the message count as fallback
        if len(user_messages) >= 2:
            logger.info("Using fallback: stage marked complete based on message count")
            return {"is_complete": True, "confidence": 70, "reason": "Fallback: sufficient messages", "extracted_data": {}}
        return {"is_complete": False, "confidence": 0, "reason": f"Error: {str(e)}", "extracted_data": {}}


async def check_stage_completion(db: Session, session_id: int) -> Dict[str, Any]:
    """
    Check if the current stage in a template consultation is complete.
    
    This function is meant to be called from the API to check stage completion
    without necessarily sending a new message.
    
    Args:
        db: Database session
        session_id: ID of the consultation session
        
    Returns:
        Dict with completion status and extracted data
    """
    # For testing/debugging - force completion if environment variable is set
    if os.getenv("DEBUG_FORCE_COMPLETION", "false").lower() == "true":
        logger.info("DEBUG_FORCE_COMPLETION enabled - forcing stage completion")
        return {"is_complete": True, "reason": "DEBUG_FORCE_COMPLETION enabled"}
        
    # Get the consultation session
    session = db.query(db_models.ConsultationSession).filter(
        db_models.ConsultationSession.id == session_id
    ).first()
    
    if not session or not session.template_id or not session.session_state:
        logger.error(f"Session {session_id} not found or not a template consultation")
        raise ValueError("Session not found or not a template consultation")
    
    # Get template data and stages
    from app.models.database_templates import ConsultationTemplate, ConsultationStage
    
    # Get current stage information
    current_stage_id = None
    
    # Try both tracking methods
    if 'current_stage' in session.session_state:
        current_stage_id = session.session_state.get('current_stage')
    elif 'current_stage_index' in session.session_state:
        # Get current stage ID from index
        current_stage_index = session.session_state.get('current_stage_index', 0)
        
        # Get all stages for the template
        stages = db.query(ConsultationStage).filter(
            ConsultationStage.template_id == session.template_id
        ).order_by(ConsultationStage.sequence_order).all()
        
        if current_stage_index < len(stages):
            current_stage_id = stages[current_stage_index].id
    
    if not current_stage_id:
        return {"is_complete": False, "reason": "No current stage set"}
    
    # Get the template
    template = db.query(ConsultationTemplate).filter(
        ConsultationTemplate.id == session.template_id
    ).first()
    
    if not template:
        logger.error(f"Template {session.template_id} not found")
        raise ValueError("Template not found")
    
    # Get current stage
    current_stage = db.query(ConsultationStage).filter(
        ConsultationStage.id == current_stage_id
    ).first()
    
    if not current_stage:
        logger.error(f"Stage {current_stage_id} not found")
        raise ValueError("Stage not found")
    
    # Format current stage data
    stage_data = {
        "id": current_stage.id,
        "name": current_stage.name,
        "description": current_stage.description,
        "stage_type": current_stage.stage_type,
        "system_instructions": current_stage.system_instructions,
        "expected_outputs": []
    }
    
    for output in current_stage.expected_outputs:
        stage_data["expected_outputs"].append({
            "name": output.name,
            "description": output.description,
            "data_type": output.data_type,
            "required": output.required
        })
    
    # Get recent messages for this stage
    messages = db.query(db_models.Message).filter(
        db_models.Message.session_id == session_id,
        db_models.Message.stage_id == current_stage_id
    ).order_by(db_models.Message.timestamp.desc()).limit(10).all()
    
    if not messages:
        return {"is_complete": False, "reason": "No messages in current stage"}
    
    # Special handling for health templates
    if template and template.domain and ("health" in template.domain.lower() or 
                                         "medical" in template.domain.lower() or 
                                         "symptom" in template.domain.lower()):
        logger.info(f"Applying health domain rules for template: {template.name}")
        
        # For health domain, we want to check for health-specific indicators in AI responses
        ai_messages = [msg for msg in messages if msg.role == "assistant"]
        if ai_messages and len(messages) >= 2:  # At least one exchange
            latest_ai_msg = ai_messages[0].content.lower()
            
            # Health-specific indicators that suggest stage completion
            health_indicators = [
                "assessment", "diagnosis", "symptoms", "condition", "treatment",
                "recommend", "analysis", "based on your", "medical history",
                "health condition", "further tests", "medication", "therapy",
                "health plan", "prognosis", "risk factors", "health record"
            ]
            
            if any(indicator in latest_ai_msg for indicator in health_indicators):
                logger.info(f"Health domain stage completion detected with indicators in AI response")
                return {"is_complete": True, "reason": "Health assessment completed"}
            
    # Count user messages - if 3 or more user messages, consider stage complete
    user_message_count = sum(1 for msg in messages if msg.role == "user")
    if user_message_count >= 3:
        logger.info(f"Stage {current_stage_id} marked complete based on message count ({user_message_count} messages)")
        return {"is_complete": True, "reason": f"Stage complete (based on {user_message_count} messages)"}
    
    # Format messages for stage completion check
    formatted_messages = []
    for message in reversed(messages):  # Reverse to get chronological order
        formatted_messages.append({
            "role": message.role,
            "content": message.content
        })
    
    # Log more detailed information about this check
    logger.info(f"Checking stage completion for session {session_id}, template: {template.name}, domain: {template.domain}")
    logger.info(f"Current stage: {current_stage.name}, Stage type: {current_stage.stage_type}")
    logger.info(f"Message count: {len(messages)}, User messages: {sum(1 for msg in messages if msg.role == 'user')}")
    
    # Check if stage is complete
    result = await detect_stage_completion(db, session_id, formatted_messages, stage_data)
    
    # Log the result
    logger.info(f"Stage completion result: {result}")
    
    return result


def force_stage_transition(db: Session, session_id: int) -> Dict[str, Any]:
    """
    Force a transition to the next stage in a template consultation.
    
    This function is used when automatic stage detection fails, allowing
    manual progression through the consultation stages.
    
    Args:
        db: Database session
        session_id: ID of the consultation session
        
    Returns:
        Dict with updated stage information
    """
    logger.info(f"Forcing stage transition for session {session_id}")
    
    # Get the consultation session
    session = db.query(db_models.ConsultationSession).filter(
        db_models.ConsultationSession.id == session_id
    ).first()
    
    if not session or not session.template_id:
        logger.error(f"Session {session_id} not found or not a template consultation")
        raise ValueError("Session not found or not a template consultation")
    
    # Import here to avoid circular imports
    from app.models.database_templates import ConsultationTemplate, ConsultationStage
    
    # Get the template
    template = db.query(ConsultationTemplate).filter(
        ConsultationTemplate.id == session.template_id
    ).first()
    
    if not template:
        logger.error(f"Template {session.template_id} not found")
        raise ValueError("Template not found")
    
    # Ensure session_state exists
    if not session.session_state:
        session.session_state = {}
    
    # Get current stage information
    current_stage_id = session.session_state.get('current_stage')
    completed_stages = session.session_state.get('completed_stages', [])
    
    # Get all stages in order
    stages = db.query(ConsultationStage).filter(
        ConsultationStage.template_id == template.id
    ).order_by(ConsultationStage.sequence_order).all()
    
    # Find current stage index
    current_stage_idx = 0
    if current_stage_id:
        for idx, stage in enumerate(stages):
            if stage.id == current_stage_id:
                current_stage_idx = idx
                break
    
    logger.info(f"Current stage index: {current_stage_idx}, total stages: {len(stages)}")
    
    # Move to next stage if possible
    if current_stage_idx + 1 < len(stages):
        next_stage = stages[current_stage_idx + 1]
        
        # Update session state
        if current_stage_id and current_stage_id not in completed_stages:
            completed_stages.append(current_stage_id)
            
        session.session_state['current_stage'] = next_stage.id
        session.session_state['completed_stages'] = completed_stages
        
        # Calculate progress percentage
        progress = ((current_stage_idx + 1) / len(stages)) * 100
        session.session_state['progress_percentage'] = progress
        
        # Save changes
        db.commit()
        
        logger.info(f"Successfully transitioned to stage {next_stage.id} ({next_stage.name})")
        
        # Return updated stage information
        return {
            "current_stage": next_stage.id,
            "current_stage_index": current_stage_idx + 1,
            "progress_percentage": progress,
            "completed_stages": completed_stages,
            "is_complete": False,
            "next_stage": {
                "id": next_stage.id,
                "name": next_stage.name,
                "description": next_stage.description,
                "type": next_stage.stage_type
            }
        }
    else:
        # Mark as complete if it was the last stage
        if current_stage_id and current_stage_id not in completed_stages:
            completed_stages.append(current_stage_id)
            
        session.session_state['completed_stages'] = completed_stages
        

async def get_ai_response(messages: list, use_rag: bool = False) -> Dict[str, Any]:
    """
    Get a response from the configured LLM provider, optionally using RAG.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        use_rag: Whether to use RAG for context augmentation
        
    Returns:
        Dictionary with response text and sources, or just a string response
    """
    try:
        # Log the LLM provider we're using
        provider_name = LLM_PROVIDER.lower() if LLM_PROVIDER else "openai"
        logger.info(f"Using LLM provider: {provider_name}")
        
        # Get the configured provider
        provider = get_llm_provider()
        
        # If using Ollama, perform environment checks
        if provider_name == "ollama":
            from app.core.config import OLLAMA_API_URL, OLLAMA_MODEL
            import socket
            from urllib.parse import urlparse
            
            # Parse the API URL
            parsed_url = urlparse(OLLAMA_API_URL)
            host = parsed_url.hostname or "localhost"
            port = parsed_url.port or 11434
            
            # Log Ollama configuration
            logger.info(f"Ollama API URL: {OLLAMA_API_URL}")
            logger.info(f"Ollama model: {OLLAMA_MODEL}")
            
            # Quick socket connectivity check
            try:
                logger.info(f"Quick connectivity check to {host}:{port}")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((host, port))
                s.close()
                logger.info(f"✓ Socket connectivity check passed")
            except Exception as socket_exc:
                logger.error(f"✗ Socket connectivity check failed: {str(socket_exc)}")
                return f"I'm having trouble connecting to the Ollama service. Please ensure Ollama is running at {host}:{port}."
        
        # Extract the user's query (last user message)
        query = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                query = msg.get("content")
                break
                
        # Generate response based on whether to use RAG
        if use_rag and query:
            # Use RAG service for enhanced responses
            logger.info(f"Using RAG for response generation with query: {query[:50]}...")
            logger.debug(f"RAG query full text: {query}")
            
            # Get RAG service and log its initialization
            rag_service = get_rag_service(provider)
            logger.info(f"RAG service retrieved, using {provider.__class__.__name__} as LLM provider")
            
            # Check for healthcare context to apply domain-specific filters
            filter_criteria = None
            healthcare_related = False
            
            # Check if any message contains healthcare keywords or if we're in a healthcare template
            for msg in messages:
                if msg.get("role") == "system" and isinstance(msg.get("content"), str):
                    if "healthcare" in msg.get("content").lower() or "hipaa" in msg.get("content").lower():
                        healthcare_related = True
                        break
            
            # Apply filter for healthcare documents if this is healthcare-related
            if healthcare_related:
                filter_criteria = {"industry": "healthcare"}
                logger.info(f"Applying healthcare-specific filter to RAG search")
            
            # Generate response with RAG, potentially with filter criteria
            logger.debug(f"Calling generate_response_with_rag with {len(messages)} messages")
            if filter_criteria:
                # Get context with sources
                logger.info(f"Retrieving healthcare-specific context with sources")
                context_obj = rag_service.get_relevant_context(query, filter_criteria=filter_criteria, include_sources=True)
                
                # Extract context text and sources
                context_text = context_obj.text if hasattr(context_obj, 'text') else str(context_obj)
                sources = context_obj.sources if hasattr(context_obj, 'sources') else []
                
                # Log source information
                if sources:
                    logger.info(f"Found {len(sources)} relevant healthcare sources")
                    for i, src in enumerate(sources):
                        metadata = src.get("metadata", {})
                        title = metadata.get("title", "Unknown")
                        source_id = metadata.get("source", "Unknown")
                        logger.info(f"  Source {i+1}: {title} ({source_id})")
                
                # Create augmented messages with the retrieved context
                augmented_messages = messages.copy()
                system_msg = next((m for m in augmented_messages if m["role"] == "system"), None)
                
                if system_msg:
                    system_msg["content"] = system_msg["content"] + f"\n\nUse the following healthcare information:\n\n{context_text}\n\nInclude source citations like [Source 1], [Source 2], etc. when referencing specific information."
                else:
                    augmented_messages.insert(0, {
                        "role": "system",
                        "content": f"You are an AI assistant specialized in healthcare SLAs and regulations. Use the following healthcare information to help answer:\n\n{context_text}\n\nInclude source citations like [Source 1], [Source 2], etc. when referencing specific information."
                    })
                
                # Generate the response with augmented messages
                response_text = await provider.generate_response(augmented_messages)
                logger.info(f"Generated response using healthcare-filtered RAG context")
                
                # Prepare response with sources
                response = {
                    "text": response_text,
                    "sources": [source.get("metadata", {}) for source in sources]
                }
            else:
                # Standard RAG flow
                response_text = await rag_service.generate_response_with_rag(messages, query)
                # No sources for standard flow
                response = {"text": response_text, "sources": []}
            
            # Log successful response generation
            if isinstance(response, dict) and "text" in response:
                logger.info(f"Successfully generated RAG response ({len(response['text'])} chars) with {len(response['sources'])} sources")
                logger.debug(f"RAG response preview: {response['text'][:100]}...")
            else:
                logger.info(f"Successfully generated RAG response ({len(response)} chars)")
                logger.debug(f"RAG response preview: {response[:100]}...")
        else:
            # Standard response generation
            logger.info(f"Calling provider.generate_response with {len(messages)} messages (standard mode)")
            response_text = await provider.generate_response(
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            # Format as consistent dictionary response
            response = {"text": response_text, "sources": []}
            logger.info(f"Successfully generated standard response ({len(response_text)} chars)")
        
        # Check if the response text is an error message from the provider
        if isinstance(response, dict) and "text" in response:
            response_text = response["text"]
            if "ollama" in response_text.lower() and any(err in response_text.lower() for err in ["error", "failed", "not", "unreachable"]):
                logger.error(f"Ollama provider returned error: {response_text}")
                error_response = f"I'm having trouble accessing my knowledge base. Technical details: {response_text}"
                return {"text": error_response, "sources": []}
        elif isinstance(response, str) and "ollama" in response.lower() and any(err in response.lower() for err in ["error", "failed", "not", "unreachable"]):
            logger.error(f"Ollama provider returned error string: {response}")
            error_response = f"I'm having trouble accessing my knowledge base. Technical details: {response}"
            return {"text": error_response, "sources": []}
            
        return response
        
    except Exception as e:
        # Log the error with traceback for debugging
        logger.error(f"Error getting AI response: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Try to provide a more specific error message
        error_str = str(e).lower()
        if "connection" in error_str or "connect" in error_str:
            return "I'm having trouble connecting to the AI service. Please check your network connection and ensure the AI service is running."
        elif "timeout" in error_str:
            return "The AI service took too long to respond. This might be due to high load or complexity of the request."
        elif "model" in error_str:
            return "There seems to be an issue with the AI model configuration. Please check that the specified model is available."
        else:
            return "I'm having trouble processing your request. Please try again later."


async def process_message(
    content: str,
    role: str,
    session_id: Optional[int],
    user_id: Optional[int],
    db: Session,
    template_id: Optional[str] = None
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
        session_type = "template" if template_id else "discovery"
        
        # Initialize session state if using a template
        session_state = {}
        if template_id:
            session_state = {
                "template_id": template_id,
                "current_stage_index": 0,
                "outputs": {},
                "status": "in_progress"
            }
        
        session = db_models.ConsultationSession(
            user_id=user_id,
            session_type=session_type,
            context_data={},
            recommendations={},
            template_id=template_id,
            session_state=session_state
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Get template data if this is a template-based session
    template_data = None
    current_stage = None
    
    if session.template_id:
        from app.models.database_templates import ConsultationTemplate, ExpectedOutput
        
        template = db.query(ConsultationTemplate).filter(
            ConsultationTemplate.id == session.template_id
        ).first()
        
        if template:
            # Format the template data for easier access
            from .prompts import get_template_system_prompt, get_stage_prompt, format_stage_message
            
            # Get the stages sorted by sequence order
            stages = sorted(template.stages, key=lambda s: s.sequence_order)
            
            # Build the template data with stages and expected outputs
            template_data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "initial_system_prompt": template.initial_system_prompt,
                "stages": []
            }
            
            # Process each stage and its expected outputs
            for stage in stages:
                # Get the expected outputs for this stage
                expected_outputs = []
                for output in stage.expected_outputs:
                    expected_outputs.append({
                        "name": output.name,
                        "description": output.description,
                        "data_type": output.data_type,
                        "required": output.required
                    })
                
                # Add the stage with its expected outputs
                template_data["stages"].append({
                    "id": stage.id,
                    "name": stage.name,
                    "description": stage.description,
                    "stage_type": stage.stage_type,
                    "prompt_template": stage.prompt_template,
                    "system_instructions": stage.system_instructions,
                    "next_stage_conditions": stage.next_stage_conditions or {},
                    "sequence_order": stage.sequence_order,
                    "expected_outputs": expected_outputs
                })
            
            # Ensure session state is properly initialized
            logger.info(f"Session state check: {session.session_state}")
            
            if not session.session_state:
                logger.info(f"Initializing session state for template {template.id}")
                # Initialize with both tracking mechanisms for compatibility
                first_stage_id = template_data["stages"][0]["id"] if template_data["stages"] else None
                session.session_state = {
                    "template_id": template.id,
                    "current_stage_index": 0,
                    "current_stage": first_stage_id,  # Add this for compatibility
                    "outputs": {},
                    "status": "in_progress"
                }
            elif isinstance(session.session_state, str):
                # Handle case where session state might be stored as a JSON string
                import json
                try:
                    session.session_state = json.loads(session.session_state)
                    logger.info(f"Converted session state from string")
                except Exception as e:
                    logger.error(f"Error parsing session state: {str(e)}")
                    # Reset the session state if it's not valid
                    # Include both tracking mechanisms for compatibility
                    first_stage_id = template_data["stages"][0]["id"] if template_data["stages"] else None
                    session.session_state = {
                        "template_id": template.id,
                        "current_stage_index": 0,
                        "current_stage": first_stage_id,  # Add this for compatibility
                        "outputs": {},
                        "status": "in_progress"
                    }
            
            db.commit()
            
            # Get the current stage based on session state
            current_stage_index = session.session_state.get("current_stage_index", 0)
            if current_stage_index < len(template_data["stages"]):
                current_stage = template_data["stages"][current_stage_index]
    
    # Update session context with detected industry if mentioned
    if role == "user" and not session.template_id:
        updated_context = detect_industry_from_message(content, session.context_data)
        if updated_context != session.context_data:
            session.context_data = updated_context
            db.commit()
    
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
    
    # Format messages for LLM API
    openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    # Add system message if not present
    if not any(msg.role == "system" for msg in messages):
        if template_data:
            # Use template-specific system prompt
            from .prompts import get_template_system_prompt
            system_prompt = get_template_system_prompt(template_data)
        else:
            # Use industry-specific prompt
            industry = None
            if session.context_data and 'industry' in session.context_data:
                industry = session.context_data.get('industry')
            
            system_prompt = get_industry_prompt(industry)
        
        system_message = {
            "role": "system", 
            "content": system_prompt
        }
        openai_messages.insert(0, system_message)
    
    # Add template-specific instructions if applicable
    if current_stage and role == "user" and template_data:
        from .prompts import get_stage_prompt
        
        # Add stage-specific instructions to guide the AI
        # Get expected outputs for the current stage
        expected_outputs = []
        for stage in template_data["stages"]:
            if stage["id"] == current_stage["id"]:
                if "expected_outputs" in stage:
                    expected_outputs = [output["name"] for output in stage["expected_outputs"]]
                break
                
        stage_instructions = {
            "role": "system",
            "content": f"""
Current stage: {current_stage['name']} ({current_stage['stage_type']})
Stage description: {current_stage['description']}
Instructions: {current_stage['system_instructions']}

Expected outputs: {', '.join(expected_outputs) if expected_outputs else 'None specified'}

Your task is to process the user's message according to this stage's requirements.
Extract the requested information and provide appropriate guidance.
"""
        }
        
        # Insert the stage instructions right before the latest user message
        insert_index = len(openai_messages) - 1
        openai_messages.insert(insert_index, stage_instructions)
    
    # Get AI response with RAG if appropriate
    # Use RAG for SLA discussions and longer conversations
    use_rag = False
    
    # Check if session is SLA-related
    if session.session_type == "discovery" or (template_data and "sla" in template_data.get("name", "").lower()):
        # Use RAG for SLA discussions
        use_rag = True
        logger.info("Using RAG for SLA-related conversation")
    
    # Check if this is a healthcare related consultation
    if template_data and "healthcare" in template_data.get("name", "").lower():
        # Always use RAG for healthcare consultations
        use_rag = True
        logger.info("Using RAG for healthcare-related consultation")
        
        # Add healthcare-specific filter criteria for the RAG service to focus on healthcare documents
        if "system_message" in locals() and isinstance(system_message, dict):
            # Update system message to instruct use of healthcare knowledge
            healthcare_context = (
                "This is a healthcare-related consultation. "
                "Focus on healthcare industry standards, HIPAA compliance, "
                "patient data security, and healthcare-specific SLA requirements. "
                "Provide detailed references to relevant healthcare regulations when applicable."
            )
            
            # Append to existing system message if it exists
            if "content" in system_message:
                system_message["content"] = system_message["content"] + "\n\n" + healthcare_context
                logger.info("Enhanced system message with healthcare-specific context")
    
    # Only use RAG after a few messages to have enough context
    if len(openai_messages) < 3:
        use_rag = False
        logger.info("Not using RAG for short conversation")
    
    # Get response with or without RAG
    response_data = await get_ai_response(openai_messages, use_rag=use_rag)
    
    # Check if we got a response with sources
    sources = []
    response_text = ""
    
    if isinstance(response_data, dict) and "text" in response_data:
        # RAG response with sources
        response_text = response_data["text"]
        sources = response_data.get("sources", [])
        logger.info(f"Received response with {len(sources)} citation sources")
    else:
        # Regular text response
        response_text = response_data
    
    # Save AI response to database
    ai_message = db_models.Message(
        session_id=session.id,
        content=response_text,
        role="assistant"
    )
    db.add(ai_message)
    
    # Update response to include sources if available
    response = response_text
    
    # Update template progression if this is a template-based session
    if current_stage and role == "user" and template_data:
        # Extract outputs from the AI response (would need advanced extraction logic)
        # For now, we'll just save the response and progress to the next stage
        
        # Store the output in the session state
        if session.session_state:
            outputs = session.session_state.get("outputs", {})
            stage_id = current_stage["id"]
            
            if stage_id not in outputs:
                outputs[stage_id] = {}
            
            outputs[stage_id]["response"] = response
            session.session_state["outputs"] = outputs
            
            # Move to the next stage
            current_stage_index = session.session_state.get("current_stage_index", 0)
            if current_stage_index + 1 < len(template_data["stages"]):
                # There are more stages, advance to the next one
                session.session_state["current_stage_index"] = current_stage_index + 1
                # Also set current_stage for compatibility with check_stage_completion
                next_stage = template_data["stages"][current_stage_index + 1]
                session.session_state["current_stage"] = next_stage["id"]
                
                # Get the next stage for additional context
                next_stage = template_data["stages"][current_stage_index + 1]
                next_stage_info = {
                    "name": next_stage["name"],
                    "type": next_stage["stage_type"],
                    "description": next_stage["description"]
                }
                
                # Include next stage info in the response
                response_with_progress = {
                    "message": response,
                    "session_id": session.id,
                    "template_progress": {
                        "completed_stage": current_stage["name"],
                        "completed_stage_index": current_stage_index,
                        "next_stage": next_stage_info,
                        "progress_percentage": (current_stage_index + 1) * 100 // len(template_data["stages"])
                    }
                }
                
                # Add sources if available
                if sources:
                    response_with_progress["sources"] = sources
                
                db.commit()
                return response_with_progress
            else:
                # This was the last stage, mark the consultation as completed
                session.session_state["status"] = "completed"
                
                # Include completion info in the response
                response_with_completion = {
                    "message": response,
                    "session_id": session.id,
                    "template_progress": {
                        "completed_stage": current_stage["name"],
                        "completed_stage_index": current_stage_index,
                        "status": "completed",
                        "progress_percentage": 100
                    }
                }
                
                # Add sources if available
                if sources:
                    response_with_completion["sources"] = sources
                
                db.commit()
                return response_with_completion
    
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
    
    # Standard response for non-template sessions
    response_obj = {
        "message": response,
        "session_id": session.id
    }
    
    # Add sources if available
    if sources:
        response_obj["sources"] = sources
    
    return response_obj