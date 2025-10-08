"""
API endpoints for consultation templates.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.template import (
    ConsultationTemplate,
    ConsultationTemplateCreate,
    ConsultationStage,
    ExpectedOutput
)
from app.models.database_templates import (
    ConsultationTemplate as DBConsultationTemplate,
    ConsultationStage as DBConsultationStage,
    ExpectedOutput as DBExpectedOutput,
    Tag as DBTag
)
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/consultation_templates",
    tags=["consultation-templates"],
    responses={404: {"description": "Not found"}},
)


def db_template_to_model(db_template: DBConsultationTemplate) -> ConsultationTemplate:
    """Convert a database template to a Pydantic model."""
    stages = []
    for stage in sorted(db_template.stages, key=lambda s: s.sequence_order):
        expected_outputs = [
            ExpectedOutput(
                name=output.name,
                description=output.description,
                data_type=output.data_type,
                required=output.required
            )
            for output in stage.expected_outputs
        ]
        
        # Normalize stage_type to ensure it's valid
        stage_type = stage.stage_type
        if stage_type == 'analysis':
            stage_type = 'problem_analysis'
        elif stage_type == 'conclusion':
            stage_type = 'summary'
        # Ensure stage_type is one of the allowed values
        if stage_type not in ["information_gathering", "problem_analysis", "recommendation", "follow_up", "summary"]:
            stage_type = "information_gathering"  # Default to a safe value
        
        stages.append(ConsultationStage(
            id=stage.id,
            name=stage.name,
            description=stage.description,
            stage_type=stage_type,
            prompt_template=stage.prompt_template,
            system_instructions=stage.system_instructions,
            expected_outputs=expected_outputs,
            ui_components=stage.ui_components or {},
            next_stage_conditions=stage.next_stage_conditions or {}
        ))
    
    return ConsultationTemplate(
        id=db_template.id,
        user_id=db_template.user_id,
        name=db_template.name,
        description=db_template.description,
        domain=db_template.domain,
        version=db_template.version,
        tags=[tag.name for tag in db_template.tags],
        initial_system_prompt=db_template.initial_system_prompt,
        stages=stages,
        is_public=db_template.is_public,
        created_at=db_template.created_at,
        updated_at=db_template.updated_at
    )


@router.get("/templates", response_model=List[ConsultationTemplate])
def get_templates(
    domain: Optional[str] = None,
    is_public: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all consultation templates."""
    query = db.query(DBConsultationTemplate)
    
    # Filter by domain if provided
    if domain:
        query = query.filter(DBConsultationTemplate.domain == domain)
    
    # Filter by public or user's own templates
    if is_public:
        query = query.filter(
            (DBConsultationTemplate.is_public == True) | 
            (DBConsultationTemplate.user_id == current_user.id)
        )
    else:
        # Only get user's templates
        query = query.filter(DBConsultationTemplate.user_id == current_user.id)
    
    templates = query.all()
    return [db_template_to_model(template) for template in templates]


@router.get("/templates/{template_id}", response_model=ConsultationTemplate)
def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific consultation template by ID."""
    template = db.query(DBConsultationTemplate).filter(DBConsultationTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if template is public or belongs to the current user
    if not template.is_public and template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this template"
        )
    
    return db_template_to_model(template)


@router.post("/templates", response_model=ConsultationTemplate)
def create_template(
    template: ConsultationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new consultation template."""
    # Create the template
    db_template = DBConsultationTemplate(
        user_id=current_user.id,
        name=template.name,
        description=template.description,
        domain=template.domain,
        version=template.version,
        initial_system_prompt=template.initial_system_prompt,
        is_public=False  # Default to private
    )
    
    db.add(db_template)
    db.flush()  # Flush to get the template ID
    
    # Process tags
    for tag_name in template.tags:
        # Check if tag exists, if not create it
        tag = db.query(DBTag).filter(DBTag.name == tag_name).first()
        if not tag:
            tag = DBTag(name=tag_name)
            db.add(tag)
            db.flush()
        
        db_template.tags.append(tag)
    
    # Create stages
    for i, stage in enumerate(template.stages):
        db_stage = DBConsultationStage(
            template_id=db_template.id,
            name=stage.name,
            description=stage.description,
            stage_type=stage.stage_type,
            prompt_template=stage.prompt_template,
            system_instructions=stage.system_instructions,
            ui_components=stage.ui_components,
            next_stage_conditions=stage.next_stage_conditions,
            sequence_order=i
        )
        
        db.add(db_stage)
        db.flush()  # Flush to get the stage ID
        
        # Create expected outputs
        for output in stage.expected_outputs:
            db_output = DBExpectedOutput(
                stage_id=db_stage.id,
                name=output.name,
                description=output.description,
                data_type=output.data_type,
                required=output.required
            )
            
            db.add(db_output)
    
    db.commit()
    
    # Refresh to get all relationships
    db.refresh(db_template)
    
    return db_template_to_model(db_template)


@router.put("/templates/{template_id}", response_model=ConsultationTemplate)
def update_template(
    template_id: str,
    template_update: ConsultationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing consultation template."""
    db_template = db.query(DBConsultationTemplate).filter(DBConsultationTemplate.id == template_id).first()
    
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if template belongs to the current user
    if db_template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this template"
        )
    
    # Update template fields
    db_template.name = template_update.name
    db_template.description = template_update.description
    db_template.domain = template_update.domain
    db_template.version = template_update.version
    db_template.initial_system_prompt = template_update.initial_system_prompt
    db_template.updated_at = datetime.utcnow()
    
    # Update tags
    # First, remove all existing tags
    db_template.tags = []
    
    # Then, add new tags
    for tag_name in template_update.tags:
        tag = db.query(DBTag).filter(DBTag.name == tag_name).first()
        if not tag:
            tag = DBTag(name=tag_name)
            db.add(tag)
            db.flush()
        
        db_template.tags.append(tag)
    
    # Update stages
    # First, delete all existing stages
    for stage in db_template.stages:
        db.delete(stage)
    
    # Then, create new stages
    for i, stage in enumerate(template_update.stages):
        db_stage = DBConsultationStage(
            template_id=db_template.id,
            name=stage.name,
            description=stage.description,
            stage_type=stage.stage_type,
            prompt_template=stage.prompt_template,
            system_instructions=stage.system_instructions,
            ui_components=stage.ui_components,
            next_stage_conditions=stage.next_stage_conditions,
            sequence_order=i
        )
        
        db.add(db_stage)
        db.flush()  # Flush to get the stage ID
        
        # Create expected outputs
        for output in stage.expected_outputs:
            db_output = DBExpectedOutput(
                stage_id=db_stage.id,
                name=output.name,
                description=output.description,
                data_type=output.data_type,
                required=output.required
            )
            
            db.add(db_output)
    
    db.commit()
    db.refresh(db_template)
    
    return db_template_to_model(db_template)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a consultation template."""
    db_template = db.query(DBConsultationTemplate).filter(DBConsultationTemplate.id == template_id).first()
    
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if template belongs to the current user
    if db_template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this template"
        )
    
    db.delete(db_template)
    db.commit()
    
    return None