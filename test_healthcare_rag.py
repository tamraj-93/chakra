#!/usr/bin/env python3
"""
Healthcare SLA RAG Test Script

This script tests the RAG integration with a set of healthcare-specific SLA questions.
It sends test queries to the RAG system and evaluates the responses.
"""

import os
import sys
import json
import asyncio
import logging
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("rag_test")

# Add the project path to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "backend"))

# Import needed modules
try:
    from app.services.llm_provider import LLMProvider
    from app.services.openai_provider import OpenAIProvider
    from app.services.ollama_provider import OllamaProvider
    from app.services.rag_service import RAGService, get_rag_service
    
    logger.info("Successfully imported project modules")
except ImportError as e:
    logger.error(f"Failed to import project modules: {str(e)}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Test questions related to healthcare SLAs
HEALTHCARE_TEST_QUESTIONS = [
    "What are the key HIPAA requirements for a healthcare SLA?",
    "What uptime should be guaranteed for critical healthcare systems?",
    "How should patient data be protected according to healthcare regulations?",
    "What incident response times should be included in a healthcare SLA?",
    "What are the security requirements for healthcare data in transit?",
    "How should a telemedicine SLA handle video quality requirements?",
    "What compliance frameworks should be referenced in a healthcare SLA?",
    "What disaster recovery provisions should be included for healthcare data?",
    "What are the best practices for healthcare application SLA metrics?",
    "How should healthcare SLAs handle third-party integrations?"
]

async def test_healthcare_questions() -> None:
    """Test RAG responses to healthcare-specific questions"""
    logger.info("=" * 60)
    logger.info("TESTING RAG WITH HEALTHCARE SLA QUESTIONS")
    logger.info("=" * 60)
    
    # Initialize providers
    try:
        # We'll use Ollama since it's already configured in the environment
        provider = OllamaProvider()
        rag_service = get_rag_service(provider)
        logger.info(f"Initialized LLM provider: {type(provider).__name__}")
    except Exception as e:
        logger.error(f"Failed to initialize providers: {str(e)}")
        return
    
    results = []
    
    # Test each question
    for i, question in enumerate(HEALTHCARE_TEST_QUESTIONS):
        logger.info(f"\nTesting question {i+1}/{len(HEALTHCARE_TEST_QUESTIONS)}")
        logger.info(f"Question: {question}")
        
        try:
            # Create a basic conversation with the question
            messages = [
                {"role": "system", "content": "You are an AI assistant specialized in healthcare SLAs and regulations."},
                {"role": "user", "content": question}
            ]
            
            # Get response using RAG
            logger.info("Generating response with RAG...")
            response = await rag_service.generate_response_with_rag(messages, question)
            
            # Get context separately to check sources
            context_with_sources = rag_service.get_relevant_context(question, include_sources=True)
            sources = []
            if hasattr(context_with_sources, 'sources'):
                sources = context_with_sources.sources
                
            logger.info(f"Found {len(sources)} relevant sources")
            
            # Log results
            logger.info("-" * 40)
            logger.info(f"Response (first 100 chars): {response[:100]}...")
            
            # Record result
            results.append({
                "question": question,
                "response": response,
                "source_count": len(sources),
                "sources": [source.get("metadata", {}) for source in sources] if sources else []
            })
            
        except Exception as e:
            logger.error(f"Error testing question: {str(e)}")
            results.append({
                "question": question,
                "error": str(e)
            })
    
    # Save results to file
    output_path = os.path.join(script_dir, "rag_test_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\nTest results saved to: {output_path}")
    logger.info(f"Tested {len(results)} questions")

    # Summarize results
    success_count = sum(1 for r in results if "error" not in r)
    logger.info(f"Successful responses: {success_count}/{len(results)}")
    
    avg_sources = sum(r.get("source_count", 0) for r in results) / len(results) if results else 0
    logger.info(f"Average sources per question: {avg_sources:.2f}")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_healthcare_questions())