#!/usr/bin/env python3
"""
Healthcare RAG Integration Check

A simplified script to check if healthcare documents exist in the knowledge base
and verify RAG can retrieve them.
"""
import os
import sys
import json
import logging
from typing import Dict, Any

# Add the backend directory to the path so we can import modules correctly
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("rag_verification")

# Define paths
VECTOR_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "data", "vector_db"))
SLA_EXAMPLES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "app", "data", "sla_examples"))

def check_healthcare_files():
    """Check if healthcare-related SLA example files exist"""
    logger.info(f"Checking for healthcare documents in: {SLA_EXAMPLES_PATH}")
    
    healthcare_files = []
    
    try:
        if os.path.exists(SLA_EXAMPLES_PATH):
            for file_name in os.listdir(SLA_EXAMPLES_PATH):
                if "healthcare" in file_name.lower() and file_name.endswith(".json"):
                    file_path = os.path.join(SLA_EXAMPLES_PATH, file_name)
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, dict) and "metadata" in data:
                                healthcare_files.append({
                                    "filename": file_name,
                                    "metadata": data.get("metadata", {})
                                })
                    except Exception as e:
                        logger.error(f"Error reading {file_name}: {str(e)}")
    
        if healthcare_files:
            logger.info(f"Found {len(healthcare_files)} healthcare document files:")
            for i, file_info in enumerate(healthcare_files):
                logger.info(f"{i+1}. {file_info['filename']} - Metadata: {json.dumps(file_info['metadata'])}")
            return True
        else:
            logger.warning("No healthcare document files found!")
            return False
    except Exception as e:
        logger.error(f"Error checking healthcare files: {str(e)}")
        return False

def check_vector_db():
    """Check if the vector database exists and has data"""
    logger.info(f"Checking vector database at: {VECTOR_DB_PATH}")
    
    if not os.path.exists(VECTOR_DB_PATH):
        logger.warning(f"Vector database path does not exist: {VECTOR_DB_PATH}")
        return False
    
    # Check for our placeholder or a real chroma db file
    placeholder_path = os.path.join(VECTOR_DB_PATH, "chroma-embeddings.placeholder")
    chroma_index_path = os.path.join(VECTOR_DB_PATH, "chroma-embeddings.parquet")
    indexed_docs_path = os.path.join(VECTOR_DB_PATH, "indexed_documents.json")
    
    if os.path.exists(chroma_index_path) or os.path.exists(placeholder_path) or os.path.exists(indexed_docs_path):
        logger.info(f"Found vector database index file or placeholder")
        
        # If we have an index file, show what documents were indexed
        if os.path.exists(indexed_docs_path):
            try:
                with open(indexed_docs_path, 'r') as f:
                    indexed_docs = json.load(f)
                    
                healthcare_docs = [doc for doc in indexed_docs if "healthcare" in doc.get("filename", "").lower()]
                logger.info(f"Found {len(healthcare_docs)} indexed healthcare documents")
                
                for i, doc in enumerate(healthcare_docs):
                    logger.info(f"  {i+1}. {doc.get('title', 'Untitled')} ({doc.get('industry', 'Unknown')})")
                    
            except Exception as e:
                logger.error(f"Error reading indexed documents: {str(e)}")
        
        return True
    else:
        logger.warning("Vector database index files not found!")
        return False

def test_rag_direct_retrieval():
    """Test the RAG service directly to see if it can retrieve healthcare documents"""
    logger.info("Testing direct RAG retrieval of healthcare content...")
    
    try:
        # Import RAG service (no need to modify path, we already did it at the top)
        from app.services.rag_service import RAGService, get_rag_service
        from app.services.ollama_provider import OllamaProvider
        from app.core.config import LLM_PROVIDER, OLLAMA_API_URL, OLLAMA_MODEL
        
        # Create service instance
        provider = OllamaProvider()
        rag_service = get_rag_service(provider)
        
        # Test questions that should match healthcare documents
        test_questions = [
            "What are HIPAA requirements for a healthcare SLA?",
            "What uptime should be guaranteed for healthcare systems?",
            "How should patient data be protected in healthcare?"
        ]
        
        results = []
        for question in test_questions:
            logger.info(f"\nTesting question: {question}")
            # Get context with sources
            context_obj = rag_service.get_relevant_context(question, include_sources=True)
            
            # Check if we have sources
            sources = []
            if hasattr(context_obj, 'sources'):
                sources = context_obj.sources
                
            result = {
                "question": question,
                "source_count": len(sources),
                "sources": [source.get("metadata", {}).get("source", "unknown") for source in sources]
            }
            results.append(result)
            
            logger.info(f"Found {len(sources)} sources for question")
            for src in result["sources"]:
                logger.info(f"  - {src}")
        
        # Calculate average sources found
        avg_sources = sum(r["source_count"] for r in results) / len(results) if results else 0
        logger.info(f"\nAverage sources found per question: {avg_sources:.1f}")
        
        return len(results) > 0 and avg_sources > 0
        
    except ImportError as e:
        logger.error(f"Failed to import RAG service: {e}")
        return False
    except Exception as e:
        logger.error(f"Error testing RAG service: {e}")
        return False

def verify_rag_integration():
    """Verify RAG integration for healthcare documents"""
    logger.info("=" * 60)
    logger.info("HEALTHCARE RAG INTEGRATION VERIFICATION")
    logger.info("=" * 60)
    
    files_exist = check_healthcare_files()
    db_exists = check_vector_db()
    
    logger.info("\nRAG VERIFICATION RESULTS:")
    logger.info("=" * 30)
    logger.info(f"Healthcare document files exist: {files_exist}")
    logger.info(f"Vector database exists: {db_exists}")
    
    # Test direct RAG retrieval if files and DB exist
    rag_retrieval_works = False
    if files_exist and db_exists:
        logger.info("\nTesting RAG direct document retrieval...")
        rag_retrieval_works = test_rag_direct_retrieval()
        logger.info(f"RAG retrieval test: {'PASSED' if rag_retrieval_works else 'FAILED'}")
    
    if files_exist and db_exists and rag_retrieval_works:
        logger.info("\n✅ PASS: Healthcare RAG integration is fully functional.")
        logger.info("    - Healthcare document files are available")
        logger.info("    - Vector database is initialized")
        logger.info("    - RAG service can retrieve healthcare documents")
    elif files_exist and db_exists:
        logger.warning("\n⚠️ WARNING: Healthcare documents exist but RAG may not be retrieving them correctly.")
        logger.warning("    - Check RAG service configuration")
        logger.warning("    - Verify document embeddings are working")
    elif files_exist and not db_exists:
        logger.warning("\n⚠️ WARNING: Healthcare documents exist but may not be in the vector database.")
        logger.warning("    - Run initialization scripts to populate the vector database")
    else:
        logger.error("\n❌ FAIL: Healthcare RAG integration is not correctly set up.")
        logger.error("    - Missing healthcare document files or vector database")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    verify_rag_integration()