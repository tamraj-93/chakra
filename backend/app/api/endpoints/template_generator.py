"""
API endpoints for template generation.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel
import logging
import random
import re

# Set up logging
logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.template_generator import convert_sla_to_template

def _generate_fallback_name(messages):
    """
    Generate a fallback service name based on message content when LLM extraction fails.
    """
    # Common service categories that might appear in SLA discussions
    service_types = [
        ("Cloud", ["aws", "azure", "gcp", "cloud", "iaas", "paas", "saas", "hosting"]),
        ("Network", ["network", "connectivity", "bandwidth", "vpn", "wan", "lan", "internet"]),
        ("Security", ["security", "firewall", "encryption", "compliance", "protection"]),
        ("Database", ["database", "db", "sql", "nosql", "data storage", "data management"]),
        ("Storage", ["storage", "backup", "archive", "object storage", "file system"]),
        ("Application", ["application", "app", "software", "platform", "saas"]),
        ("API", ["api", "interface", "endpoint", "integration", "microservice"]),
        ("Infrastructure", ["infrastructure", "server", "datacenter", "hardware", "compute"]),
        ("Web", ["website", "web", "ecommerce", "online", "portal"]),
        ("Support", ["support", "help desk", "service desk", "customer service"])
    ]
    
    if not messages or len(messages) == 0:
        # No messages, use a generic name
        return "Generic SLA Template"
        
    # Try to find a match in the conversation
    conversation_text = " ".join([msg.content.lower() for msg in messages[:5] if hasattr(msg, 'content')])
    
    # Check for domain-specific keywords first
    domains = {
        "Healthcare": ["healthcare", "medical", "health", "patient", "hospital", "clinic", "ehr", "hipaa"],
        "Financial": ["financial", "banking", "payment", "transaction", "money", "finance", "bank"],
        "Retail": ["retail", "ecommerce", "shop", "store", "sales", "customer"],
        "Telecom": ["telecom", "telecommunication", "voice", "mobile", "telephony"],
        "IT": ["it service", "information technology", "tech support"]
    }
    
    # Check for domain match
    domain_matches = []
    for domain, keywords in domains.items():
        for keyword in keywords:
            if keyword in conversation_text:
                domain_matches.append(domain)
                break
    
    # If we have domain matches, use the first one
    if domain_matches:
        primary_domain = domain_matches[0]
        
        # Now look for service type within that domain
        for service_type, keywords in service_types:
            for keyword in keywords:
                if keyword in conversation_text:
                    return f"{primary_domain} {service_type} SLA"
        
        # If no service type found, just use the domain
        return f"{primary_domain} Services SLA"
    
    # Look for specific patterns like "X service" or "Y platform"
    service_patterns = [
        r'(\w+)\s+(service|platform|infrastructure|application|system|solution)',
        r'(cloud|network|database|storage|security)\s+(\w+)',
        r'sla\s+for\s+(\w+\s+\w+)',
        r'(api|application|platform|system)\s+(\w+)',
    ]
    
    for pattern in service_patterns:
        matches = re.findall(pattern, conversation_text)
        if matches:
            # Use the first match
            if isinstance(matches[0], tuple):
                service_name = " ".join(matches[0]).title()
            else:
                service_name = matches[0].title()
            return f"{service_name} SLA"
    
    # Look for any of the common service types in the conversation
    for service_type, keywords in service_types:
        for keyword in keywords:
            if keyword in conversation_text:
                return f"{service_type} Services SLA"
    
    # Fall back to a generic name with a timestamp identifier
    import datetime
    now = datetime.datetime.now()
    date_str = now.strftime("%b %d")
    return f"SLA Consultation ({date_str})"

router = APIRouter(
    prefix="/template_generator",
    tags=["template-generator"],
    responses={404: {"description": "Not found"}},
)

class TemplateGenerationRequest(BaseModel):
    session_id: int
    template_name: str
    template_description: str = None
    domain: str = "SLA"
    is_public: bool = False

@router.post("/convert-sla", response_model=Dict[str, Any])
async def convert_sla_consultation_to_template(
    request: TemplateGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Convert an SLA consultation session into a reusable template.
    This endpoint uses LLM to analyze the conversation flow and create a structured template.
    """
    try:
        result = await convert_sla_to_template(
            session_id=request.session_id,
            db=db,
            template_name=request.template_name,
            template_description=request.template_description,
            domain=request.domain,
            is_public=request.is_public
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating template: {str(e)}"
        )

@router.get("/eligible-sessions", response_model=List[Dict[str, Any]])
async def get_eligible_sla_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of consultation sessions that are eligible for conversion to SLA templates.
    This endpoint identifies sessions that appear to be SLA consultations based on content.
    """
    from app.models.database import ConsultationSession, Message
    from sqlalchemy import func
    
    # Get all discovery sessions for the current user
    sessions = db.query(ConsultationSession).filter(
        ConsultationSession.user_id == current_user.id,
        ConsultationSession.session_type == "discovery"
    ).all()
    
    eligible_sessions = []
    for session in sessions:
        # Check if this session has SLA-related content
        sla_mentions = db.query(func.count(Message.id)).filter(
            Message.session_id == session.id,
            Message.content.ilike("%SLA%") | 
            Message.content.ilike("%service level%") |
            Message.content.ilike("%agreement%")
        ).scalar()
        
        if sla_mentions > 0:
            # Get the first few messages for context
            first_messages = db.query(Message).filter(
                Message.session_id == session.id
            ).order_by(Message.id).limit(5).all()
            
            # Use LLM to extract a specific service name from the conversation
            from app.services.ai import get_llm_provider
            
            service_name = "SLA Consultation"
            template_name = None
            
            # Look for template name in session state first
            if session.session_state and isinstance(session.session_state, dict):
                if "topic" in session.session_state:
                    topic = session.session_state.get("topic")
                    if topic:
                        service_name = f"{topic.title()} SLA"
                elif "service_name" in session.session_state:
                    service_name = session.session_state.get("service_name")
                elif "template_name" in session.session_state:
                    template_name = session.session_state.get("template_name")
            
            # If we couldn't find it in session state, use LLM to extract from messages
            if not template_name and len(first_messages) > 0:
                try:
                    # Combine message content for analysis
                    conversation_text = "\n".join([msg.content for msg in first_messages])
                    
                    # Ask LLM to extract the specific service name
                    provider = get_llm_provider()
                    prompt = f"""
                    Extract the specific service name or topic being discussed in this SLA consultation.
                    Be specific and precise - don't just return "SLA" or "Service Level Agreement".
                    For example, if discussing network uptime requirements, return "Network Infrastructure Services".
                    If discussing a cloud database, return "Cloud Database Services".
                    
                    Conversation:
                    {conversation_text[:1000]}  # Limit to first 1000 chars
                    
                    Extract ONLY the service name, with no additional text. Do not include phrases like "extracted service name is" in your response.
                    """
                    
                    # Create a better prompt to get a specific, concise service name
                    extract_prompt = [
                        {"role": "system", "content": "You are a service name extractor. RESPOND ONLY WITH 2-3 WORDS. Do not include phrases like 'Service' or 'SLA' in your response. Extract only the core domain like 'Cloud Database' or 'Network Infrastructure'. Never explain, justify or add context to your response."},
                        {"role": "user", "content": "Extract a short service name (2-3 words max) from this conversation about an SLA. Example good responses: 'Cloud Storage', 'Database Hosting', 'API Gateway', 'Healthcare Records'.\n\nConversation:\n" + conversation_text[:800]}
                    ]
                    
                    # Use LLM to extract the name
                    response = provider.generate_response_sync(extract_prompt)
                    
                    # Clean up the response
                    extracted_name = response.strip()
                    
                    # Process the extracted name
                    if extracted_name:
                        # Remove common prefixes and clean the response
                        extracted_name = extracted_name.strip('"\'.,;:()[]{}').strip()
                        
                        # Simple word count check - we want 1-3 words
                        word_count = len(extracted_name.split())
                        
                        # Check for valid length and word count
                        if 1 <= word_count <= 5 and len(extracted_name) <= 30:
                            # Add "SLA" to the end if it's not already there
                            if "SLA" not in extracted_name.upper():
                                service_name = f"{extracted_name} SLA"
                            else:
                                service_name = extracted_name
                                
                            logger.info(f"LLM extracted service name: {service_name}")
                        else:
                            # Try to extract something useful from the conversation
                            service_name = _generate_fallback_name(first_messages)
                            logger.warning(f"LLM returned invalid name (too long): '{extracted_name}'. Using fallback: {service_name}")
                    else:
                        # Use fallback name generation
                        service_name = _generate_fallback_name(first_messages)
                        logger.warning(f"LLM returned empty service name. Using fallback: {service_name}")
                except Exception as e:
                    logger.error(f"Error extracting service name with LLM: {e}")
                    
                    # Fallback to keyword matching if LLM extraction fails
                    topic_keywords = ["cloud", "database", "network", "healthcare", "financial", 
                                     "security", "application", "infrastructure", "storage", "backup"]
                    
                    for msg in first_messages:
                        content = msg.content.lower()
                        for keyword in topic_keywords:
                            if f"{keyword} sla" in content or f"sla for {keyword}" in content:
                                service_name = f"{keyword.title()} Service SLA"
                                break
            
            # Create a session summary
            summary = {
                "id": session.id,
                "created_at": session.created_at,
                "name": template_name or service_name,
                "message_count": db.query(func.count(Message.id)).filter(
                    Message.session_id == session.id
                ).scalar(),
                "sla_relevance": "high" if sla_mentions > 3 else "medium",
                "preview": first_messages[0].content[:100] + "..." if first_messages else "",
            }
            eligible_sessions.append(summary)
    
    return eligible_sessions
    
@router.get("/session-details/{session_id}", response_model=Dict[str, Any])
async def get_session_details(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific consultation session.
    This endpoint returns the complete conversation history and context data.
    """
    from app.models.database import ConsultationSession, Message
    
    # Check if session exists and belongs to this user
    session = db.query(ConsultationSession).filter(
        ConsultationSession.id == session_id,
        ConsultationSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied"
        )
    
    # Get all messages for this session
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.id).all()
    
    # Format response
    return {
        "id": session.id,
        "created_at": session.created_at,
        "user_id": session.user_id,
        "messages": [
            {
                "id": msg.id,
                "content": msg.content,
                "role": msg.role,
                "timestamp": msg.timestamp
            }
            for msg in messages
        ],
        "context_data": session.context_data
    }