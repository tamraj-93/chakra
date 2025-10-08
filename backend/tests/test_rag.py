#!/usr/bin/env python
"""
Unit tests for the RAG implementation
"""

import sys
import os
import unittest
from unittest import mock
import logging

# Add the parent directory to the path so we can import our app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Disable INFO logging for cleaner test output
logging.basicConfig(level=logging.WARNING)

class TestVectorStore(unittest.TestCase):
    """Test cases for the VectorStore class."""
    
    def test_singleton_pattern(self):
        """Test that VectorStore follows singleton pattern."""
        from app.services.vector_store import get_vector_store
        
        # Get two instances
        store1 = get_vector_store()
        store2 = get_vector_store()
        
        # Check they're the same instance
        self.assertIs(store1, store2)

    @mock.patch('app.services.vector_store.SentenceTransformer')
    def test_add_and_search_documents(self, mock_transformer):
        """Test adding documents and searching them."""
        # Mock the embedding model to avoid loading actual model
        mock_model = mock.MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3, 0.4]]  # Mock embeddings
        mock_transformer.return_value = mock_model
        
        from app.services.vector_store import get_vector_store
        
        # Reset the singleton for clean test
        from app.services.vector_store import VectorStore
        VectorStore._instance = None
        
        # Get a fresh instance with our mocked transformer
        store = get_vector_store()
        
        # Replace the real collection with a mock
        mock_collection = mock.MagicMock()
        store.collection = mock_collection
        
        # Test adding documents
        documents = [
            {"content": "This is a test document about cloud databases."}
        ]
        metadata = [
            {"source": "test", "industry": "it"}
        ]
        
        store.add_documents(documents, metadata)
        
        # Verify document was processed and added
        mock_collection.add.assert_called_once()
        
        # Mock search results
        mock_collection.query.return_value = {
            "documents": [["This is a test document about cloud databases."]],
            "metadatas": [[{"source": "test", "industry": "it", "chunk_id": "doc_0_chunk_0"}]],
            "distances": [[0.2]]
        }
        
        # Test searching
        results = store.search("cloud database", top_k=1)
        
        # Verify search was performed
        mock_collection.query.assert_called_once()
        
        # Verify results format
        self.assertEqual(len(results), 1)
        self.assertIn("content", results[0])
        self.assertIn("metadata", results[0])
        self.assertIn("score", results[0])
        self.assertEqual(results[0]["content"], "This is a test document about cloud databases.")

class TestDocumentProcessor(unittest.TestCase):
    """Test cases for the DocumentProcessor class."""
    
    def test_extract_metadata(self):
        """Test metadata extraction from document content."""
        from app.services.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Create a mock document with healthcare content
        content = "This is a healthcare SLA document for HIPAA compliance and patient data security."
        file_path = "/test/healthcare_sla.txt"
        
        # Mock the elements
        class MockTitle:
            def __str__(self):
                return "Healthcare SLA Document"
        
        elements = [MockTitle()]
        
        # Extract metadata
        metadata = processor._extract_metadata(file_path, content, elements)
        
        # Verify extracted metadata
        self.assertEqual(metadata["title"], "Healthcare SLA Document")
        self.assertEqual(metadata["industry"], "healthcare")
        self.assertEqual(metadata["file_type"], "txt")
        self.assertIn("HIPAA", metadata.get("compliance_frameworks", []))

class TestRAGService(unittest.TestCase):
    """Test cases for the RAG service."""
    
    @mock.patch('app.services.rag_service.get_vector_store')
    @mock.patch('app.services.rag_service.get_document_processor')
    def test_get_relevant_context(self, mock_get_processor, mock_get_store):
        """Test retrieving relevant context for a query."""
        # Set up mocks
        mock_store = mock.MagicMock()
        mock_get_store.return_value = mock_store
        
        mock_processor = mock.MagicMock()
        mock_get_processor.return_value = mock_processor
        
        # Mock search results
        mock_store.search.return_value = [
            {
                "content": "Cloud Database SLA ensures 99.99% uptime with 100ms response time.",
                "metadata": {"source": "cloud_db_sla.json"},
                "score": 0.9
            },
            {
                "content": "Response times for API calls should be under 300ms for 95% of requests.",
                "metadata": {"source": "api_sla.json"},
                "score": 0.8
            }
        ]
        
        # Import and initialize RAG service
        from app.services.rag_service import RAGService
        from app.services.llm_provider import LLMProvider
        
        # Create a mock LLM provider
        mock_llm = mock.MagicMock(spec=LLMProvider)
        
        # Initialize the service
        rag_service = RAGService(mock_llm)
        
        # Test getting context
        context = rag_service.get_relevant_context("What are standard response times for databases?")
        
        # Verify search was performed
        mock_store.search.assert_called_once()
        
        # Verify context contains expected information
        self.assertIn("Cloud Database SLA", context)
        self.assertIn("99.99% uptime", context)
        self.assertIn("100ms response time", context)
        self.assertIn("API calls", context)
        self.assertIn("300ms", context)

if __name__ == "__main__":
    unittest.main()