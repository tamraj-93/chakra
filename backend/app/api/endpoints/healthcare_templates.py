"""
API endpoints for healthcare-specific templates.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import os
import json

from app.services.healthcare_template_service import HealthcareTemplateService
from app.api.dependencies.auth import get_current_user

router = APIRouter()
template_service = HealthcareTemplateService()

@router.get("/")
async def get_healthcare_templates():
    """Get all healthcare templates"""
    try:
        templates = template_service.get_healthcare_templates()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading healthcare templates: {str(e)}")

@router.get("/{template_id}")
async def get_healthcare_template(template_id: str):
    """Get a specific healthcare template by ID"""
    try:
        template = template_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Healthcare template not found: {template_id}")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading healthcare template: {str(e)}")

@router.get("/categories")
async def get_healthcare_categories():
    """Get available healthcare template categories"""
    return {
        "categories": [
            {"id": "ehr", "name": "EHR Systems", "description": "Electronic Health Record system templates"},
            {"id": "telemedicine", "name": "Telemedicine", "description": "Templates for virtual healthcare services"},
            {"id": "security", "name": "Healthcare Security", "description": "Templates focusing on healthcare data security"},
            {"id": "hipaa", "name": "HIPAA Compliance", "description": "Templates for ensuring HIPAA compliance"}
        ]
    }