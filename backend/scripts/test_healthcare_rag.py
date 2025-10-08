#!/usr/bin/env python
"""
Healthcare RAG System Test Script

This script tests the RAG system with healthcare-specific queries to verify
that the system correctly retrieves and incorporates healthcare domain knowledge
into its responses.

Usage:
    python test_healthcare_rag.py

Requirements:
    - The RAG system must be initialized using initialize_rag.py
    - Healthcare SLA examples must be loaded into the vector store
"""

import os
import sys
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add the parent directory to the path so we can import our app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vector_store import get_vector_store
from app.services.document_processor import get_document_processor
from app.services.rag_service import RAGService
from app.core.config import LLM_PROVIDER
from app.services.llm_provider import LLMProvider
from app.services.openai_provider import OpenAIProvider
from app.services.ollama_provider import OllamaProvider

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_llm_provider() -> LLMProvider:
    """Get the configured LLM provider."""
    provider_name = LLM_PROVIDER.lower() if LLM_PROVIDER else "openai"
    
    if provider_name == "ollama":
        from app.core.config import OLLAMA_API_URL, OLLAMA_MODEL
        return OllamaProvider(
            api_url=OLLAMA_API_URL,
            model=OLLAMA_MODEL
        )
    else:
        from app.core.config import OPENAI_API_KEY
        return OpenAIProvider(api_key=OPENAI_API_KEY)

def verify_rag_initialized() -> bool:
    """Verify that the RAG system has been initialized."""
    vector_store = get_vector_store()
    count = vector_store.get_document_count()
    
    if count == 0:
        logger.error("Vector store is empty. Please run initialize_rag.py first.")
        return False
    
    logger.info(f"Vector store contains {count} documents.")
    return True

def test_healthcare_queries(rag_service: RAGService):
    """Test the RAG service with healthcare-specific queries."""
    healthcare_queries = [
        {
            "query": "What uptime percentage should a healthcare application guarantee?",
            "expected_keywords": ["99.9", "99.95", "99.99", "uptime", "healthcare", "availability"],
            "description": "Testing healthcare application uptime SLA knowledge"
        },
        {
            "query": "What are the HIPAA compliance requirements for a healthcare SLA?",
            "expected_keywords": ["HIPAA", "encryption", "PHI", "compliance", "audit", "breach", "notification"],
            "description": "Testing HIPAA compliance knowledge"
        },
        {
            "query": "What should the response time be for healthcare application database queries?",
            "expected_keywords": ["response time", "second", "millisecond", "database", "query"],
            "description": "Testing healthcare performance metrics knowledge"
        },
        {
            "query": "What should be included in a disaster recovery plan for healthcare applications?",
            "expected_keywords": ["disaster", "recovery", "backup", "RTO", "RPO", "failover"],
            "description": "Testing disaster recovery knowledge for healthcare"
        },
        {
            "query": "What are appropriate service credit levels for healthcare SLA violations?",
            "expected_keywords": ["service credit", "monthly fee", "percentage", "violation", "uptime"],
            "description": "Testing service credit knowledge for healthcare"
        },
        # Added telemedicine-specific queries
        {
            "query": "What video quality standards should be specified in a telemedicine SLA?",
            "expected_keywords": ["HD", "720p", "frame rate", "fps", "audio-video sync", "bandwidth"],
            "description": "Testing telemedicine video quality standards knowledge"
        },
        {
            "query": "What are the key security requirements for patient data in healthcare systems?",
            "expected_keywords": ["encryption", "AES-256", "multi-factor", "authentication", "audit", "HIPAA"],
            "description": "Testing patient data security knowledge"
        },
        {
            "query": "How should a telemedicine platform handle clinical workflow during technical issues?",
            "expected_keywords": ["failover", "backup", "offline mode", "recovery", "alternative", "zero data loss"],
            "description": "Testing telemedicine clinical continuity knowledge"
        },
        {
            "query": "What healthcare integration standards should be supported by a telemedicine platform?",
            "expected_keywords": ["HL7", "FHIR", "EHR", "integration", "medical device", "API"],
            "description": "Testing healthcare integration standards knowledge"
        },
        {
            "query": "What encryption standards are required for healthcare data at rest?",
            "expected_keywords": ["AES-256", "encryption", "key management", "NIST", "FIPS"],
            "description": "Testing healthcare data encryption knowledge"
        }
    ]
    
    results = []
    
    print(f"{Colors.HEADER}{Colors.BOLD}\nTesting Healthcare RAG Functionality{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    for i, test_case in enumerate(healthcare_queries, 1):
        print(f"\n{Colors.BOLD}Test Case {i}: {test_case['description']}{Colors.ENDC}")
        print(f"{Colors.BLUE}Query: {test_case['query']}{Colors.ENDC}")
        
        # Get context from vector store
        context = rag_service.get_relevant_context(test_case['query'])
        
        # Generate response using RAG
        response = rag_service.generate_response(test_case['query'])
        
        # Check for expected keywords
        found_keywords = []
        missing_keywords = []
        
        for keyword in test_case['expected_keywords']:
            if keyword.lower() in response.lower():
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate score based on found keywords
        score = len(found_keywords) / len(test_case['expected_keywords']) * 100
        
        # Determine status
        if score >= 80:
            status = f"{Colors.GREEN}PASS{Colors.ENDC}"
        elif score >= 50:
            status = f"{Colors.YELLOW}PARTIAL{Colors.ENDC}"
        else:
            status = f"{Colors.RED}FAIL{Colors.ENDC}"
        
        print(f"{Colors.CYAN}Found keywords ({len(found_keywords)}/{len(test_case['expected_keywords'])}): {', '.join(found_keywords)}{Colors.ENDC}")
        
        if missing_keywords:
            print(f"{Colors.YELLOW}Missing keywords: {', '.join(missing_keywords)}{Colors.ENDC}")
        
        print(f"Status: {status} - Score: {score:.1f}%\n")
        print(f"{Colors.GREEN}Response:{Colors.ENDC}\n{response}\n")
        print(f"{Colors.BOLD}{'-'*80}{Colors.ENDC}")
        
        # Store results
        results.append({
            "query": test_case['query'],
            "description": test_case['description'],
            "response": response,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "score": score,
            "status": "PASS" if score >= 80 else "PARTIAL" if score >= 50 else "FAIL"
        })
    
    # Generate summary
    passes = sum(1 for r in results if r['status'] == "PASS")
    partials = sum(1 for r in results if r['status'] == "PARTIAL")
    failures = sum(1 for r in results if r['status'] == "FAIL")
    total_score = sum(r['score'] for r in results) / len(results)
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}Healthcare RAG Test Results Summary{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"Total test cases: {len(results)}")
    print(f"{Colors.GREEN}Passed: {passes}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Partial: {partials}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {failures}{Colors.ENDC}")
    print(f"Overall score: {total_score:.1f}%")
    
    # Save results to file
    results_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "tests",
        "results"
    )
    
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(results_dir, f"healthcare_rag_test_{timestamp}.json")
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_cases": len(results),
            "passes": passes,
            "partials": partials,
            "failures": failures,
            "overall_score": total_score,
            "results": results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")

def main():
    """Main function to run the tests."""
    print(f"{Colors.BOLD}{Colors.HEADER}Healthcare RAG Testing Tool{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    # Verify RAG is initialized
    if not verify_rag_initialized():
        print(f"\n{Colors.RED}ERROR: RAG system is not initialized. Please run initialize_rag.py first.{Colors.ENDC}")
        return False
    
    # Get LLM provider
    llm_provider = get_llm_provider()
    
    # Initialize RAG service
    rag_service = RAGService(llm_provider)
    
    # Run tests
    test_healthcare_queries(rag_service)
    
    return True

if __name__ == "__main__":
    main()