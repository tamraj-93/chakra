from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
import os
import shutil
import re

from app.services.healthcare_classifier import HealthcareDocumentClassifier

router = APIRouter()

# Healthcare-specific constants
HEALTHCARE_INDUSTRIES = [
    "Healthcare - General",
    "Hospital",
    "Telemedicine",
    "Health Insurance",
    "Pharmaceutical",
    "Medical Devices",
    "Laboratory Services",
    "Mental Health",
    "Home Healthcare",
    "Long-term Care"
]

HEALTHCARE_SERVICE_TYPES = [
    "EHR Hosting",
    "Telemedicine Platform",
    "Patient Portal",
    "Health Information Exchange",
    "Medical Imaging Storage",
    "Healthcare Analytics",
    "Clinical Decision Support",
    "Remote Patient Monitoring",
    "E-Prescribing",
    "Healthcare API Services"
]

HEALTHCARE_COMPLIANCE_TYPES = [
    "HIPAA",
    "HITECH",
    "42 CFR Part 2",
    "GDPR for Health",
    "State Healthcare Privacy Laws",
    "Joint Commission",
    "HITRUST CSF",
    "SOC 2 for Healthcare",
    "FDA Compliance",
    "Medicare/Medicaid Compliance"
]

# Data Models
class Document(BaseModel):
    id: str
    filename: str
    title: str
    industry: Optional[str] = None
    service_type: Optional[str] = None
    upload_date: str
    file_size: int
    status: str  # processed, pending, error
    
    # Healthcare-specific fields
    healthcare_category: Optional[str] = None
    compliance_frameworks: Optional[List[str]] = None
    clinical_specialties: Optional[List[str]] = None
    data_sensitivity: Optional[str] = None

# Mock storage - in a real app, this would be in a database
documents = []

# Directory to store uploaded files
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[Document])
async def get_documents(
    industry: Optional[str] = None,
    service_type: Optional[str] = None,
    healthcare_category: Optional[str] = None,
    compliance_framework: Optional[str] = None,
    clinical_specialty: Optional[str] = None,
    data_sensitivity: Optional[str] = None
):
    """Get list of all documents with healthcare-specific filtering options"""
    filtered_docs = documents
    
    # Apply filters if specified
    if industry:
        filtered_docs = [doc for doc in filtered_docs if doc.get("industry") == industry]
    
    if service_type:
        filtered_docs = [doc for doc in filtered_docs if doc.get("service_type") == service_type]
    
    if healthcare_category:
        filtered_docs = [doc for doc in filtered_docs if doc.get("healthcare_category") == healthcare_category]
        
    if compliance_framework:
        filtered_docs = [doc for doc in filtered_docs if doc.get("compliance_frameworks") and 
                        compliance_framework in doc.get("compliance_frameworks", [])]
    
    if clinical_specialty:
        filtered_docs = [doc for doc in filtered_docs if doc.get("clinical_specialties") and 
                        clinical_specialty in doc.get("clinical_specialties", [])]
    
    if data_sensitivity:
        filtered_docs = [doc for doc in filtered_docs if doc.get("data_sensitivity") == data_sensitivity]
    
    return filtered_docs

@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: str):
    """Get a specific document by ID"""
    for doc in documents:
        if doc["id"] == document_id:
            return doc
    raise HTTPException(status_code=404, detail="Document not found")

@router.post("/upload")
async def upload_document(
    files: List[UploadFile] = File(...),
    industry: Optional[str] = Form(None),
    service_type: Optional[str] = Form(None),
    healthcare_category: Optional[str] = Form(None),
    compliance_frameworks: Optional[str] = Form(None),  # Comma-separated values
    clinical_specialties: Optional[str] = Form(None),   # Comma-separated values
    data_sensitivity: Optional[str] = Form(None)
):
    """Upload one or more documents with healthcare-specific metadata"""
    result = []
    for file in files:
        # Generate unique ID and determine file size
        doc_id = str(uuid.uuid4())
        content = await file.read()
        file_size = len(content)
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Process content for healthcare classification
        content_str = content.decode('utf-8', errors='ignore')
        healthcare_metadata = extract_healthcare_metadata(content_str, file.filename)
        
        # Create document record
        document = {
            "id": doc_id,
            "filename": file.filename,
            "title": os.path.splitext(file.filename)[0],
            "upload_date": datetime.now().isoformat(),
            "file_size": file_size,
            "status": "processed",  # In a real app, this would be "pending" until processed
            
            # Add industry from form or auto-detected
            "industry": industry or healthcare_metadata.get("industry"),
            "service_type": service_type or healthcare_metadata.get("service_type"),
            
            # Add healthcare-specific fields
            "healthcare_category": healthcare_category or healthcare_metadata.get("healthcare_category"),
            "compliance_frameworks": (
                compliance_frameworks.split(",") if compliance_frameworks 
                else healthcare_metadata.get("compliance_frameworks")
            ),
            "clinical_specialties": (
                clinical_specialties.split(",") if clinical_specialties 
                else healthcare_metadata.get("clinical_specialties")
            ),
            "data_sensitivity": data_sensitivity or healthcare_metadata.get("data_sensitivity")
        }
        documents.append(document)
        result.append(document)
        
    return {"message": f"Successfully uploaded {len(files)} documents", "documents": result}

# Create classifier instance
healthcare_classifier = HealthcareDocumentClassifier()

def extract_healthcare_metadata(content: str, filename: str) -> Dict[str, Any]:
    """Extract healthcare-specific metadata from document content using the classifier"""
    # Use the classifier to extract detailed healthcare metadata
    classification = healthcare_classifier.classify_document(content, filename)
    
    # Convert to the format expected by our API
    metadata = {
        "industry": classification.get("industry"),
        "service_type": classification.get("service_type"),
        "healthcare_category": classification.get("healthcare_category"),
        "compliance_frameworks": classification.get("compliance_frameworks", []),
        "clinical_specialties": classification.get("clinical_specialties", []),
        "data_sensitivity": classification.get("data_sensitivity")
    }
    
    return metadata

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    for idx, doc in enumerate(documents):
        if doc["id"] == document_id:
            # Remove from list
            deleted = documents.pop(idx)
            
            # Delete file if exists
            file_path = os.path.join(UPLOAD_DIR, f"{document_id}_{deleted['filename']}")
            if os.path.exists(file_path):
                os.remove(file_path)
                
            return {"message": "Document deleted successfully"}
            
    raise HTTPException(status_code=404, detail="Document not found")

@router.get("/metadata/options")
async def get_metadata_options():
    """Get available healthcare metadata options for filtering and classification"""
    return {
        "industries": HEALTHCARE_INDUSTRIES,
        "service_types": HEALTHCARE_SERVICE_TYPES,
        "compliance_frameworks": HEALTHCARE_COMPLIANCE_TYPES,
        "clinical_specialties": [
            "Cardiology", "Radiology", "Pediatrics", "Oncology", 
            "Neurology", "Orthopedics", "Primary Care", "Emergency Medicine", 
            "Surgery", "Obstetrics/Gynecology", "Psychiatry", "Dermatology"
        ],
        "healthcare_categories": [
            "Clinical Information Systems",
            "Administrative Systems",
            "Virtual Care",
            "Analytics and Reporting",
            "Patient Engagement",
            "Research",
            "Population Health Management",
            "Care Coordination"
        ],
        "data_sensitivity_levels": ["Low", "Medium", "High", "Critical"]
    }