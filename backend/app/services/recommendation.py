"""
Template recommendation service.
This service provides recommendations for SLA templates based on user requirements.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging
from app.models import database as db_models
from app.services import ai as ai_service
from app.services.prompts import get_template_recommendation_prompt
from app.services.llm_provider import LLMProvider
from app.core.config import LLM_PROVIDER
from app.services.openai_provider import OpenAIProvider
from app.services.ollama_provider import OllamaProvider

# Set up logging
logger = logging.getLogger(__name__)

def get_llm_provider() -> LLMProvider:
    """Get the configured LLM provider based on settings."""
    if LLM_PROVIDER.lower() == "openai":
        return OpenAIProvider()
    else:
        return OllamaProvider()

async def get_template_recommendations(
    db: Session,
    user_requirements: Dict[str, Any],
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Get template recommendations based on user requirements.
    
    Args:
        db: Database session
        user_requirements: Dict containing user's requirements (service type, industry, description)
        limit: Maximum number of recommendations to return
        
    Returns:
        List of recommended templates with similarity scores
    """
    try:
        # Extract key information from user requirements
        service_type = user_requirements.get("service_type", "")
        description = user_requirements.get("description", "")
        industry = user_requirements.get("industry", "")
        
        # Log the request
        logger.info(f"Generating template recommendations for: {service_type} in {industry or 'any industry'}")
        
        # Get all available templates
        available_templates = db.query(db_models.SLATemplate).filter(
            db_models.SLATemplate.is_public == True
        ).all()
        
        if not available_templates:
            logger.warning("No public templates available for recommendations")
            return []
            
        # If we have a direct match for industry and service type, prioritize those
        direct_matches = [
            t for t in available_templates 
            if t.service_type == service_type and 
               (not industry or t.industry == industry)
        ]
        
        if direct_matches and len(direct_matches) >= limit:
            logger.info(f"Found {len(direct_matches)} direct matches for recommendations")
            # Return top matches based on direct attribute matching
            recommendations = [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.template_data.get("description", ""),
                    "industry": t.industry,
                    "service_type": t.service_type,
                    "similarity_score": 100,  # Direct match gets top score
                    "match_reason": f"Perfect match for {t.service_type} in {t.industry} industry"
                }
                for t in direct_matches[:limit]
            ]
            return recommendations
            
        # If no direct matches or not enough, use LLM to recommend templates
        # Construct a prompt for the LLM to analyze
        llm_provider = get_llm_provider()
        
        # Get all templates to send to LLM
        template_data = []
        for i, template in enumerate(available_templates[:10]):  # Limit to 10 templates to avoid context length issues
            template_data.append({
                "id": template.id,
                "name": template.name,
                "industry": template.industry,
                "service_type": template.service_type,
                "description": template.template_data.get("description", "No description")
            })
            
        # Create prompt for LLM
        system_prompt = get_template_recommendation_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
User requirements:
- Service Type: {service_type}
- Industry: {industry or 'Not specified'}
- Description: {description}

Available templates:
{template_data}

Please provide {limit} template recommendations based on the user requirements.
Format your response as a valid JSON array of objects with fields:
id, name, similarity_score (0-100), match_reason
"""
            }
        ]
        
        # Generate recommendations using LLM
        try:
            response = await llm_provider.generate_response(messages, temperature=0.2)
            logger.debug(f"LLM recommendation response: {response[:200]}...")
            
            # Extract JSON from response (handle potential text before/after JSON)
            import json
            import re
            
            # Extract JSON array using regex
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if not json_match:
                logger.warning("Failed to extract JSON from LLM response")
                return []
                
            recommendations_json = json.loads(json_match.group(0))
            
            # Enhance recommendations with additional template data
            enhanced_recommendations = []
            for rec in recommendations_json:
                template_id = rec.get("id")
                template = next((t for t in available_templates if t.id == template_id), None)
                
                if template:
                    enhanced_recommendations.append({
                        "id": template.id,
                        "name": template.name,
                        "description": template.template_data.get("description", ""),
                        "industry": template.industry,
                        "service_type": template.service_type,
                        "similarity_score": rec.get("similarity_score", 0),
                        "match_reason": rec.get("match_reason", "")
                    })
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error generating template recommendations with LLM: {str(e)}")
            
            # Fallback: Return templates based on matching service_type
            fallback_matches = [
                t for t in available_templates 
                if t.service_type == service_type
            ]
            
            # If still no matches, return any templates
            if not fallback_matches:
                fallback_matches = available_templates
                
            recommendations = [
                {
                    "id": t.id,
                    "name": t.name, 
                    "description": t.template_data.get("description", ""),
                    "industry": t.industry,
                    "service_type": t.service_type,
                    "similarity_score": 70 if t.service_type == service_type else 50,
                    "match_reason": "Matching service type" if t.service_type == service_type else "General template"
                }
                for t in fallback_matches[:limit]
            ]
            
            return recommendations
            
    except Exception as e:
        logger.error(f"Error in template recommendations: {str(e)}")
        return []