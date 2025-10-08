"""
Template Generator Service

This service provides functionality to convert SLA consultations into reusable templates
using LLM assistance to extract structured conversation flows.
"""
import logging
import uuid
import json
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.models.database import ConsultationSession, Message
from app.models.database_templates import (
    ConsultationTemplate, ConsultationStage, 
    ExpectedOutput, Tag
)
from app.services.llm_provider import LLMProvider
from app.core.config import LLM_PROVIDER
from app.services.openai_provider import OpenAIProvider
from app.services.ollama_provider import OllamaProvider

# Set up logging
logger = logging.getLogger(__name__)

def get_llm_provider() -> LLMProvider:
    """Get the appropriate LLM provider based on configuration."""
    if LLM_PROVIDER.lower() == "openai":
        return OpenAIProvider()
    else:
        return OllamaProvider()

def analyze_conversation_structure(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract template structure from completed consultation.
    
    This function analyzes conversation messages to identify natural stages,
    required inputs, expected outputs, and system prompts. It uses LLM
    assistance to structure the conversation into a reusable template.
    
    Args:
        messages: List of messages from the consultation
        
    Returns:
        Dictionary with extracted template structure
    """
    logger.info("Analyzing conversation structure to extract template")
    
    if not messages:
        raise ValueError("No messages provided for analysis")
    
    # Get LLM provider
    llm_provider = get_llm_provider()
    
    # Prepare messages for analysis
    formatted_messages = []
    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        formatted_messages.append(f"{role.upper()}: {content}")
    
    # Create prompt for conversation analysis
    analysis_prompt = f"""
    You are analyzing a consultation conversation to extract a structured template.
    
    Your task is to:
    1. Identify natural stages in the conversation
    2. For each stage, determine:
       - Stage name and purpose
       - Required inputs
       - Expected outputs
       - System instructions for the AI
    3. Include ALL relevant content from the conversation in your analysis
    4. Ensure each stage has a clear purpose and progression
    
    Below is the conversation transcript:
    
    {formatted_messages}
    
    IMPORTANT: Include ALL key information from the conversation in your template.
    Each stage should have complete system instructions that capture the full context.
    
    Please analyze this conversation and structure it as a template with distinct stages.
    Format your response as a JSON object with the following structure:
    
    ```json
    {{
      "initial_system_prompt": "System prompt for the entire consultation",
      "stages": [
        {{
          "name": "Stage Name",
          "description": "Description of this stage's purpose",
          "stage_type": "information_gathering|problem_analysis|recommendation|follow_up|summary",
          "prompt_template": "Question or prompt to start this stage",
          "system_instructions": "Instructions for the AI in this stage",
          "expected_outputs": [
            {{
              "name": "output_name",
              "description": "Description of this output",
              "data_type": "text|number|boolean|list|object",
              "required": true/false
            }}
          ]
        }}
      ]
    }}
    ```
    
    Only respond with the JSON. No other text.
    """
    
    # Generate analysis
    try:
        analysis_response = llm_provider.generate_response([
            {"role": "system", "content": "You are a specialized AI for analyzing conversations and creating structured templates."},
            {"role": "user", "content": analysis_prompt}
        ])
        
        # Extract JSON from response
        try:
            # Find JSON block in response if it exists
            if "```json" in analysis_response:
                json_text = analysis_response.split("```json")[1].split("```")[0]
            else:
                json_text = analysis_response
                
            template_structure = json.loads(json_text.strip())
            
            # Log success
            logger.info(f"Successfully extracted template structure with {len(template_structure.get('stages', []))} stages")
            
            # Return the template structure
            return template_structure
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing template structure response: {str(e)}")
            logger.error(f"Raw response: {analysis_response}")
            raise ValueError("Failed to parse template structure from LLM response")
            
    except Exception as e:
        logger.error(f"Error analyzing conversation structure: {str(e)}")
        raise ValueError(f"Failed to analyze conversation structure: {str(e)}")


async def convert_sla_to_template(
    session_id: int, 
    db: Session, 
    template_name: str,
    template_description: str = None,
    domain: str = "SLA",
    is_public: bool = False
) -> Dict[str, Any]:
    """
    Convert an SLA consultation session into a reusable template.
    
    Args:
        session_id: The ID of the consultation session to convert
        db: Database session
        template_name: Name for the new template
        template_description: Description for the new template (optional)
        domain: Domain for the template (default: SLA)
        is_public: Whether the template should be public (default: False)
        
    Returns:
        Dictionary with information about the created template
    """
    # Get consultation session and messages
    session = db.query(ConsultationSession).filter(ConsultationSession.id == session_id).first()
    if not session:
        raise ValueError(f"No consultation session found with ID {session_id}")
    
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.id).all()
    if not messages:
        raise ValueError(f"No messages found for consultation session {session_id}")
    
    # Convert db messages to dict format for analysis
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "role": msg.role,
            "content": msg.content,
            "stage_id": msg.stage_id
        })
    
    logger.info(f"Analyzing conversation structure for session {session_id} with {len(formatted_messages)} messages")
    
    # Analyze conversation structure to extract template
    try:
        template_structure = analyze_conversation_structure(formatted_messages)
        
        # Extract key components from the template structure
        initial_system_prompt = template_structure.get("initial_system_prompt", "")
        stages = template_structure.get("stages", [])
        
        if not stages:
            raise ValueError("No stages were identified in the conversation")
        
        logger.info(f"Extracted {len(stages)} stages from conversation")
    except Exception as e:
        logger.error(f"Error analyzing conversation structure: {str(e)}")
        raise ValueError(f"Failed to analyze consultation: {str(e)}")
        
        # Create template object
        template_id = str(uuid.uuid4())
        
        template = ConsultationTemplate(
            id=template_id,
            user_id=session.user_id,
            name=template_name,
            description=template_description or f"Template generated from consultation session #{session_id}",
            domain=domain,
            version="1.0.0",
            initial_system_prompt=initial_system_prompt,
            is_public=is_public
        )
        
        # Add tags
        if domain.lower() == "sla":
            tags = ["SLA", "Service Level Agreement"]
            
            # Look for additional industry tags
            content_text = " ".join([msg.content.lower() for msg in messages])
            if "cloud" in content_text:
                tags.append("Cloud Services")
            if "healthcare" in content_text:
                tags.append("Healthcare")
            if "financial" in content_text or "banking" in content_text:
                tags.append("Financial Services")
            if "retail" in content_text or "e-commerce" in content_text:
                tags.append("Retail")
        else:
            tags = [domain]
        
        template_tags = []
        for tag_name in tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            template_tags.append(tag)
        
        template.tags = template_tags
        
        # Create stages
        db_stages = []
        for i, stage_data in enumerate(stages):
            # Create expected outputs for this stage
            expected_outputs = []
            for output_data in stage_data.get("expected_outputs", []):
                expected_output = ExpectedOutput(
                    name=output_data.get("name", f"output_{i}_{len(expected_outputs)}"),
                    description=output_data.get("description", ""),
                    data_type=output_data.get("data_type", "text"),
                    required=output_data.get("required", True)
                )
                expected_outputs.append(expected_output)
            
            # Create the stage
            stage = ConsultationStage(
                id=str(uuid.uuid4()),
                template_id=template_id,
                name=stage_data.get("name", f"Stage {i+1}"),
                description=stage_data.get("description", ""),
                stage_type=stage_data.get("stage_type", "information_gathering"),
                prompt_template=stage_data.get("prompt_template", ""),
                system_instructions=stage_data.get("system_instructions", ""),
                sequence_order=i,
                ui_components=stage_data.get("ui_components", {})
            )
            
            # Attach the expected outputs to the stage
            stage.expected_outputs = expected_outputs
            db_stages.append(stage)
        
        # Save everything to the database
        db.add(template)
        for stage in db_stages:
            db.add(stage)
        
        db.commit()
        
        # Return template info
        return {
            "template_id": template_id,
            "name": template.name,
            "stages_count": len(db_stages),
            "tags": [tag.name for tag in template_tags]
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating template from consultation: {str(e)}")
        raise ValueError(f"Failed to create template: {str(e)}")
        
        stage = ConsultationStage(
            id=str(uuid.uuid4()),
            template_id=template_id,
            name=stage_data["name"],
            description=stage_data["description"],
            stage_type=stage_data["type"],
            prompt_template=stage_data["prompt"],
            system_instructions=stage_data.get("system_instructions", ""),
            sequence_order=i,
            ui_components=stage_data.get("ui_components", {})
        )
        
        stage.expected_outputs = expected_outputs
        db_stages.append(stage)
    
    # Save everything to the database
    db.add(template)
    for stage in db_stages:
        db.add(stage)
    
    db.commit()
    
    return {
        "template_id": template_id,
        "name": template.name,
        "stages_count": len(db_stages),
        "tags": [tag.name for tag in template_tags]
    }

async def identify_conversation_stages(
    llm: LLMProvider,
    messages: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Use LLM to identify distinct stages in the conversation.
    
    Args:
        llm: LLM provider instance
        messages: List of message dictionaries
        
    Returns:
        List of stage dictionaries
    """
    prompt = f"""
    You are analyzing a conversation about Service Level Agreements (SLAs) to identify distinct stages 
    that can be used to create a reusable consultation template. Your task is to:

    1. Identify 3-5 logical stages in the conversation
    2. For each stage, define:
       - A name (short, descriptive)
       - A description (what this stage accomplishes)
       - The type (information_gathering, problem_analysis, recommendation, follow_up, or summary)
       - A prompt template that can guide this stage of the conversation
       - A list of expected outputs (structured data to collect)

    Review this conversation and create the template stages:
    
    {format_messages_for_prompt(messages)}
    
    Output should be in this JSON format:
    ```json
    [
      {{
        "name": "Stage Name",
        "description": "Stage description",
        "type": "stage_type",
        "prompt": "Prompt template",
        "system_instructions": "Additional instructions for the AI",
        "expected_outputs": [
          {{
            "name": "output_name",
            "description": "What this output represents",
            "data_type": "string|number|boolean|array|object",
            "required": true
          }}
        ],
        "ui_components": {{
          "structured_input": {{
            "fields": [
              {{
                "id": "field_id",
                "label": "Field Label",
                "type": "text|textarea|select|radio|checkbox",
                "options": [
                  {{ "value": "option1", "label": "Option 1" }}
                ],
                "placeholder": "Enter value",
                "required": true,
                "help_text": "Help text"
              }}
            ],
            "prompt": "Please provide the following information"
          }}
        }}
      }}
    ]
    ```
    
    Each stage should build logically on the previous one, and the stages should cover the entire consultation process.
    """
    
    response = await llm.generate_response([{"role": "user", "content": prompt}])
    
    # Extract JSON from the response
    import json
    import re
    
    # Find JSON content between triple backticks
    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find any JSON array in the response
        json_match = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            logger.error(f"Could not extract JSON from LLM response: {response}")
            json_str = "[]"
    
    try:
        stages = json.loads(json_str)
        return stages
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from LLM response: {str(e)}")
        return []

async def generate_system_prompt(
    llm: LLMProvider,
    messages: List[Dict[str, Any]],
    domain: str
) -> str:
    """
    Generate a system prompt for the template based on the conversation.
    
    Args:
        llm: LLM provider instance
        messages: List of message dictionaries
        domain: The domain for the template
        
    Returns:
        System prompt string
    """
    prompt = f"""
    Create a concise system prompt that will guide an AI assistant through a {domain} consultation. 
    The prompt should establish the AI's role, expertise, and approach based on this conversation:
    
    {format_messages_for_prompt(messages)}
    
    The system prompt should:
    1. Define the AI's role (expert in {domain})
    2. Establish the consultation purpose
    3. Set the tone and approach
    4. Outline the general process to follow
    
    Generate ONLY the system prompt text, without explanations or meta-commentary.
    """
    
    response = await llm.generate_response([{"role": "user", "content": prompt}])
    
    # Clean up the response to get just the system prompt
    # Remove any markdown formatting or explanations
    import re
    
    # Remove markdown code blocks
    response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
    
    # Remove explanations like "Here's a system prompt:" or "System Prompt:"
    response = re.sub(r'^.*?(System Prompt:?|Here\'s a system prompt:?)', '', response, flags=re.DOTALL).strip()
    
    return response

def format_messages_for_prompt(messages: List[Dict[str, Any]]) -> str:
    """Format messages for inclusion in a prompt."""
    formatted = ""
    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"]
        formatted += f"{role}: {content}\n\n"
    return formatted