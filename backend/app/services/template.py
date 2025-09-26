from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.models import database as db_models

def create_template(
    db: Session,
    user_id: int,
    name: str,
    industry: str,
    service_type: str,
    template_data: Dict[str, Any],
    is_public: bool = False
):
    """Create a new SLA template."""
    template = db_models.SLATemplate(
        user_id=user_id,
        name=name,
        industry=industry,
        service_type=service_type,
        template_data=template_data,
        is_public=is_public
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

def get_template(db: Session, template_id: int):
    """Get a specific SLA template."""
    return db.query(db_models.SLATemplate).filter(
        db_models.SLATemplate.id == template_id
    ).first()

def get_templates(
    db: Session,
    user_id: Optional[int] = None,
    industry: Optional[str] = None,
    service_type: Optional[str] = None,
    is_public: bool = True
):
    """Get SLA templates with optional filtering."""
    query = db.query(db_models.SLATemplate)
    
    # Apply filters
    if user_id:
        query = query.filter(db_models.SLATemplate.user_id == user_id)
    if industry:
        query = query.filter(db_models.SLATemplate.industry == industry)
    if service_type:
        query = query.filter(db_models.SLATemplate.service_type == service_type)
    
    # Always filter for public templates or user's own templates
    if user_id:
        query = query.filter(
            (db_models.SLATemplate.is_public == is_public) | 
            (db_models.SLATemplate.user_id == user_id)
        )
    else:
        query = query.filter(db_models.SLATemplate.is_public == is_public)
    
    return query.all()

def get_metrics(db: Session, category: Optional[str] = None):
    """Get SLA metrics with optional category filtering."""
    query = db.query(db_models.SLAMetric)
    
    if category:
        query = query.filter(db_models.SLAMetric.category == category)
    
    return query.all()

def generate_document(template_id: int, customizations: Dict[str, Any] = None):
    """Generate a document from a template with optional customizations."""
    # This would integrate with a document generation service
    # For now, we'll return a placeholder
    return {
        "document_url": f"https://example.com/documents/{template_id}",
        "format": "pdf"
    }