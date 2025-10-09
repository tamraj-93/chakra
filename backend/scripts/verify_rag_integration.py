#!/usr/bin/env python3
"""
Verify RAG Integration for Healthcare

This script checks:
1. If healthcare documents are in the knowledge base
2. Tests a healthcare query against the RAG system
3. Validates RAG service integration with AI service
"""
import os
import sys
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("rag_verification")

# Add backend directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(backend_dir)

from app.services.ai import get_llm_provider  # Import from ai.py instead
from app.services.rag_service import get_rag_service, get_healthcare_document_count
from app.services.ai import get_ai_response


async def test_rag_healthcare_integration():
    """Test RAG integration with healthcare documents"""
    logger.info("=" * 50)
    logger.info("VERIFYING RAG HEALTHCARE INTEGRATION")
    logger.info("=" * 50)
    
    # Check healthcare documents
    healthcare_doc_count = get_healthcare_document_count()
    logger.info(f"Healthcare documents in knowledge base: {healthcare_doc_count}")
    
    if healthcare_doc_count == 0:
        logger.warning("No healthcare documents found! RAG may not work effectively for healthcare queries.")
    else:
        logger.info(f"Found {healthcare_doc_count} healthcare documents - RAG should function properly.")
    
    # Test a healthcare query using RAG directly
    llm_provider = get_llm_provider()
    rag_service = get_rag_service(llm_provider)
    
    test_query = "What are the key HIPAA requirements for healthcare SLAs?"
    logger.info(f"Testing direct RAG query: '{test_query}'")
    
    # Get context from RAG
    context = rag_service.get_relevant_context(
        test_query, 
        filter_criteria={"metadata.industry": "healthcare"}
    )
    
    if not context:
        logger.warning("No context retrieved for healthcare query!")
    else:
        logger.info(f"Retrieved {len(context)} chars of context for healthcare query")
        logger.info("Context preview: " + context[:200] + "...")
    
    # Test using the AI service with RAG
    logger.info("Testing AI service with RAG for healthcare query...")
    messages = [
        {"role": "system", "content": "You are an assistant specializing in healthcare SLAs."},
        {"role": "user", "content": test_query}
    ]
    
    response = await get_ai_response(messages, use_rag=True)
    
    if response:
        logger.info(f"AI service with RAG generated a response ({len(response)} chars)")
        logger.info("Response preview: " + response[:200] + "...")
    else:
        logger.error("AI service with RAG failed to generate a response!")
    
    logger.info("=" * 50)
    logger.info("RAG VERIFICATION COMPLETE")
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_rag_healthcare_integration())