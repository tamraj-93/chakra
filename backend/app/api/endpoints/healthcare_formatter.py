from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional
import os
from datetime import datetime
import json

from app.services.healthcare_sla_formatter import HealthcareSLAFormatter

router = APIRouter()

# Initialize the SLA formatter
healthcare_formatter = HealthcareSLAFormatter()

@router.post("/format")
async def format_healthcare_sla(
    sla_data: Dict[str, Any] = Body(...),
    output_format: str = Query("markdown", description="Output format (markdown, html, or json)")
):
    """
    Format healthcare SLA data into a document with appropriate healthcare-specific sections
    """
    try:
        # Generate formatted SLA document
        result = healthcare_formatter.format_sla(sla_data, output_format)
        
        return {
            "status": "success",
            "message": f"SLA formatted successfully in {output_format} format",
            "file_path": result["file_path"],
            "filename": result["filename"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error formatting SLA: {str(e)}")

@router.get("/download/{filename}")
async def download_healthcare_sla(filename: str):
    """
    Download a previously generated healthcare SLA document
    """
    try:
        # Validate filename to prevent directory traversal attacks
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
            
        # Get output directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "output")
        file_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        # Determine media type based on file extension
        media_types = {
            ".md": "text/markdown",
            ".html": "text/html",
            ".json": "application/json",
            ".txt": "text/plain"
        }
        
        extension = os.path.splitext(filename)[1].lower()
        media_type = media_types.get(extension, "application/octet-stream")
        
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.get("/templates")
async def get_healthcare_sla_templates():
    """
    Get available healthcare SLA templates for formatting
    """
    templates = [
        {
            "id": "ehr_hosting",
            "name": "EHR Hosting SLA",
            "description": "Template for Electronic Health Record hosting services",
            "category": "Clinical Information Systems"
        },
        {
            "id": "telemedicine",
            "name": "Telemedicine Platform SLA",
            "description": "Template for telemedicine and virtual care platforms",
            "category": "Virtual Care"
        },
        {
            "id": "hipaa_security",
            "name": "HIPAA Security SLA",
            "description": "Template focusing on HIPAA Security Rule compliance",
            "category": "Security & Compliance"
        }
    ]
    
    return templates