"""
API endpoints for healthcare-specific consultations.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.models import consultation as consultation_models
from app.api.dependencies.auth import get_current_user
from app.services.healthcare_template_service import HealthcareTemplateService

router = APIRouter()
template_service = HealthcareTemplateService()

@router.post("/start")
async def start_healthcare_consultation(
    template_id: str,
    message: consultation_models.MessageBase,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start a consultation using a healthcare template"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting healthcare consultation with template ID: {template_id}")
        logger.info(f"Message content: {message.content}")
        
        # Load the healthcare template
        template = template_service.get_template_by_id(template_id)
        logger.info(f"Template found: {template is not None}")
        
        if not template:
            logger.error(f"Healthcare template not found: {template_id}")
            raise HTTPException(status_code=404, detail=f"Healthcare template not found: {template_id}")
            
        logger.info(f"Template data: {template}")
        
        # Create a consultation session manually
        from app.models import database as db_models
        
        # Create session with healthcare template data
        session_state = {
            "template_id": template_id,
            "current_stage": None,  # Will be set based on template
            "completed_stages": [],
            "progress_percentage": 0,
            "extracted_data": {},
            "is_healthcare_template": True  # Mark as healthcare template
        }
        
        # Create the session in the database
        db_session = db_models.ConsultationSession(
            user_id=current_user.id if current_user else None,
            session_type="healthcare_template",
            context_data={},
            recommendations={},
            template_id=template_id,
            session_state=session_state
        )
        
        # Add and commit to database
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        # If template has stages, set up the first stage
        stages = template.get("stages", [])
        logger.info(f"Template has {len(stages)} stages")
        
        if stages and len(stages) > 0:
            # Set the first stage as current
            first_stage = stages[0]
            stage_id = first_stage.get("id", "stage_1") if isinstance(first_stage, dict) else "stage_1"
            logger.info(f"Setting first stage to: {stage_id}")
            db_session.session_state["current_stage"] = stage_id
            db.commit()
        
        # Return session info
        session = {
            "id": db_session.id,
            "current_stage": db_session.session_state.get("current_stage")
        }
        
        # Return the session ID and initial message
        return {
            "message": "Healthcare consultation started successfully",
            "session_id": session["id"],
            "template": template["name"]
        }
        
    except Exception as e:
        import traceback
        logger.error(f"Error starting healthcare consultation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error starting healthcare consultation: {str(e)}")