#!/usr/bin/env python3
"""
Minimal Healthcare RAG Test Script

This script provides a minimal way to test the RAG system with healthcare queries,
with minimal dependencies. It directly tests the vector database and embeddings.

Usage: python3 minimal_test_healthcare_rag.py
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Colored output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_header(text):
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}{text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}{text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}{text}{Colors.ENDC}")

def main():
    print_header("=" * 70)
    print_header("            MINIMAL HEALTHCARE RAG TEST")
    print_header("=" * 70)

    # Import necessary modules
    try:
        import chromadb
        print_success("✓ Successfully imported chromadb")
    except ImportError:
        print_error("Error: chromadb not installed. Install with: pip install chromadb")
        return False

    try:
        from sentence_transformers import SentenceTransformer
        print_success("✓ Successfully imported sentence_transformers")
    except ImportError:
        print_error("Error: sentence_transformers not installed. Install with: pip install sentence-transformers")
        return False

    # Create a test vector store
    print_header("\nSetting up test vector store...")
    persist_dir = os.path.join("data", "test_vector_db")
    os.makedirs(persist_dir, exist_ok=True)
    
    try:
        client = chromadb.PersistentClient(path=persist_dir)
        print_success("✓ ChromaDB client created successfully")
    except Exception as e:
        print_error(f"Error creating ChromaDB client: {e}")
        return False
    
    # Create an embedding function
    try:
        embedding_fn = SentenceTransformer('all-MiniLM-L6-v2')
        print_success("✓ Embedding model loaded successfully")
    except Exception as e:
        print_error(f"Error loading embedding model: {e}")
        return False
    
    # Create or get a collection
    try:
        collection = client.get_or_create_collection(
            name="test_healthcare_sla",
            embedding_function=lambda texts: embedding_fn.encode(texts).tolist()
        )
        print_success("✓ Collection created successfully")
    except Exception as e:
        print_error(f"Error creating collection: {e}")
        return False
    
    # Add some healthcare test documents
    print_header("\nAdding healthcare test documents...")
    
    # Simple healthcare SLA examples
    healthcare_docs = [
        {
            "content": "Healthcare SLA - Uptime: 99.99% guaranteed for healthcare applications. All systems must comply with HIPAA regulations.",
            "metadata": {"industry": "healthcare", "type": "uptime"}
        },
        {
            "content": "Patient data must be encrypted at rest with AES-256 encryption. All PHI transmissions require TLS 1.2 or higher.",
            "metadata": {"industry": "healthcare", "type": "security"}
        },
        {
            "content": "Telemedicine platform must support HD video (720p) quality with 25fps minimum frame rate. Audio-video sync within 50ms.",
            "metadata": {"industry": "healthcare", "type": "telemedicine"}
        },
        {
            "content": "Healthcare application response time SLA: 2 seconds for web pages, 1 second for database queries, 5 seconds for reports.",
            "metadata": {"industry": "healthcare", "type": "performance"}
        }
    ]
    
    try:
        # Clear the collection first
        collection.delete(collection.get()["ids"])
        
        # Add documents
        collection.add(
            documents=[doc["content"] for doc in healthcare_docs],
            metadatas=[doc["metadata"] for doc in healthcare_docs],
            ids=[f"doc_{i}" for i in range(len(healthcare_docs))]
        )
        print_success(f"✓ Added {len(healthcare_docs)} healthcare documents to the vector store")
    except Exception as e:
        print_error(f"Error adding documents: {e}")
        return False
    
    # Test queries
    print_header("\nTesting healthcare RAG queries...")
    
    test_queries = [
        "What uptime should healthcare applications guarantee?",
        "How should patient data be encrypted?",
        "What video quality is required for telemedicine?",
        "What are the response time requirements for healthcare applications?"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\nQuery {i+1}: {query}")
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=2
            )
            
            print_success("Results:")
            for doc, meta, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similarity = 1 - min(distance, 1.0)
                print(f"- Similarity: {similarity:.2f}")
                print(f"  Document: {doc}")
                print(f"  Metadata: {meta}")
                print()
                
        except Exception as e:
            print_error(f"Error querying vector store: {e}")
    
    print_success("\nTest completed successfully!")
    print_header("=" * 70)
    return True

if __name__ == "__main__":
    main()