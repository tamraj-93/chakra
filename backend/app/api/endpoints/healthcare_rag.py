from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import os

from app.services.healthcare_rag import HealthcareRAGSystem

router = APIRouter()

# Initialize the RAG system
DOCUMENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "documents")
healthcare_rag = HealthcareRAGSystem(DOCUMENT_DIR)

# Data models
class SearchResult(BaseModel):
    chunk_id: str
    doc_id: str
    document_title: str
    document_filename: str
    chunk_text: str
    relevance_score: float

class Citation(BaseModel):
    doc_id: str
    document_title: str
    document_filename: str
    relevance_score: float

class RAGResponse(BaseModel):
    answer: str
    citations: List[Citation]
    context_used: Optional[List[Dict[str, Any]]] = None

@router.get("/search", response_model=List[SearchResult])
async def search_documents(
    query: str = Query(..., description="The search query"),
    top_k: int = Query(5, description="Number of results to return")
):
    """Search healthcare documents for relevant information"""
    try:
        # Initialize if not already initialized
        if not healthcare_rag.initialized:
            healthcare_rag.initialize()
            
        # Perform search
        results = healthcare_rag.search(query, top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@router.get("/ask", response_model=RAGResponse)
async def ask_healthcare_question(
    question: str = Query(..., description="The healthcare SLA question")
):
    """Ask a question about healthcare SLAs using RAG"""
    try:
        # Initialize if not already initialized
        if not healthcare_rag.initialized:
            healthcare_rag.initialize()
            
        # Generate response with citations
        response = healthcare_rag.generate_with_citations(question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.post("/initialize")
async def initialize_rag_system():
    """Initialize or refresh the RAG system"""
    try:
        result = healthcare_rag.initialize()
        return {"status": "success", "message": "RAG system initialized", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing RAG system: {str(e)}")

@router.get("/health")
async def check_rag_health():
    """Check the health status of the RAG system"""
    return {
        "status": "healthy",
        "initialized": healthcare_rag.initialized,
        "document_count": len(healthcare_rag.document_store) if healthcare_rag.initialized else 0,
        "vector_store_size": len(healthcare_rag.vector_store) if healthcare_rag.initialized else 0
    }