from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.core.database import get_db
from app.models import consultation as consultation_models
from app.models import database as db_models
from app.models import sla as sla_models
from app.services import ai as ai_service
from app.services import pdf_generator
from app.services import recommendation as recommendation_service
from app.api.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/templates",
    tags=["templates"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=sla_models.SLATemplate, status_code=status.HTTP_201_CREATED)
async def create_template(template_data: Dict[str, Any], db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Create a new SLA template for the authenticated user"""
    # Create the template in the database
    new_template = db_models.SLATemplate(
        user_id=current_user.id,
        name=template_data.get("name", "New SLA Template"),
        industry=template_data.get("industry"),
        service_type=template_data.get("service_type"),
        template_data=template_data,
        is_public=template_data.get("is_public", False)
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return new_template

@router.get("/", response_model=List[sla_models.SLATemplate])
async def get_templates(
    industry: str = None, 
    service_type: str = None,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Get templates with optional filtering"""
    # Start with a base query
    query = db.query(db_models.SLATemplate)
    
    # Filter by user (include the user's templates + public templates)
    query = query.filter(
        (db_models.SLATemplate.user_id == current_user.id) | 
        (db_models.SLATemplate.is_public == True)
    )
    
    # Apply optional filters
    if industry:
        query = query.filter(db_models.SLATemplate.industry == industry)
    
    if service_type:
        query = query.filter(db_models.SLATemplate.service_type == service_type)
    
    # Execute the query
    templates = query.all()
    
    return templates

@router.get("/{template_id}", response_model=sla_models.SLATemplate)
async def get_template(template_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get a specific template by ID (must be owned by the user or public)"""
    # Query for the template
    template = db.query(db_models.SLATemplate).filter(
        db_models.SLATemplate.id == template_id,
        ((db_models.SLATemplate.user_id == current_user.id) | 
         (db_models.SLATemplate.is_public == True))
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template

@router.get("/metrics", response_model=List[sla_models.SLAMetric])
async def get_metrics(category: str = None, db: Session = Depends(get_db)):
    """Get SLA metrics with optional category filtering"""
    # Start with a base query
    query = db.query(db_models.SLAMetric)
    
    # Apply optional category filter
    if category:
        query = query.filter(db_models.SLAMetric.category == category)
    
    # Execute the query
    metrics = query.all()
    
    return metrics

@router.post("/generate", response_model=Dict[str, str])
async def generate_template(
    data: Dict[str, Any], 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate a new SLA template document based on specified parameters"""
    try:
        # Use the template service to generate the document
        service_name = data.get("service_name", "Untitled Service")
        service_type = data.get("service_type", "web_application")
        description = data.get("description", "")
        metrics = data.get("metrics", [])
        
        # In a real implementation, this would generate a document
        # For now, we'll simulate the process
        # The real implementation would use the template_service to generate
        
        # Create a file path based on the service name
        safe_name = service_name.lower().replace(" ", "_")
        template_url = f"/api/templates/download/{safe_name}_sla.docx"
        
        # Return the URL to the generated document
        return {"template_url": template_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Template generation failed: {str(e)}"
        )
        
@router.get("/{template_id}/export", status_code=200)
async def export_template(
    template_id: int, 
    format: str = "pdf", 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Export a template as PDF or Word document"""
    # Query for the template
    template = db.query(db_models.SLATemplate).filter(
        db_models.SLATemplate.id == template_id,
        ((db_models.SLATemplate.user_id == current_user.id) | 
         (db_models.SLATemplate.is_public == True))
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Generate a filename based on the template name
    safe_name = template.name.lower().replace(" ", "_").replace("/", "_")
    
    if format.lower() == "pdf":
        # Generate PDF content
        try:
            # Convert template to dictionary with proper data structure for PDF generator
            template_dict = {
                "id": template.id,
                "name": template.name,
                "description": getattr(template, "description", ""),
                "industry": template.industry,
                "service_type": template.service_type,
                "template_data": template.template_data,
                "created_at": str(template.created_at) if hasattr(template, "created_at") else ""
            }
            
            pdf_content = pdf_generator.generate_sla_pdf(template_dict)
            
            # Return the PDF as base64 string that frontend can decode
            return {"filename": f"{safe_name}.pdf", "content": pdf_content, "format": "pdf"}
        except Exception as e:
            import logging
            logging.error(f"PDF generation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
    
    elif format.lower() == "docx":
        # We could implement Word document generation here
        # For now, return an error
        raise HTTPException(status_code=400, detail="DOCX format not implemented yet")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid format specified. Supported formats: pdf, docx")
        
@router.post("/recommend", response_model=List[Dict[str, Any]])
async def recommend_templates(
    requirements: Dict[str, Any], 
    limit: int = 3,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Recommend templates based on user requirements.
    
    Args:
        requirements: Dictionary with service_type, description, and optional industry
        limit: Maximum number of recommendations to return
        
    Returns:
        List of recommended templates with similarity scores and match reasons
    """
    try:
        recommendations = await recommendation_service.get_template_recommendations(
            db=db,
            user_requirements=requirements,
            limit=limit
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Template recommendation failed: {str(e)}"
        )