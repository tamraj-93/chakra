"""
Document Processor - Demo Mode
Mock document processor for demo environments that doesn't require heavy dependencies

This module provides document loading and processing capabilities without
requiring the unstructured package or other heavy dependencies.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Export this function for compatibility with the imported module
def partition(*args, **kwargs):
    """Mock function for unstructured.partition.auto.partition"""
    logger.info("Mock partition function called")
    return []

class SimpleDocumentProcessor:
    """A simplified document processor for demo mode"""
    
    def __init__(self):
        self.supported_extensions = {
            ".txt": self._process_text,
            ".md": self._process_markdown,
            ".json": self._process_json,
            ".html": self._process_html,
            ".pdf": self._mock_pdf_processing,
            ".doc": self._mock_doc_processing,
            ".docx": self._mock_doc_processing,
        }
    
    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a document file and return a list of content chunks
        
        Args:
            file_path: Path to the document to process
            
        Returns:
            List of document chunks with text and metadata
        """
        _, ext = os.path.splitext(file_path.lower())
        
        if ext not in self.supported_extensions:
            logger.warning(f"Unsupported file extension: {ext}, using generic processor")
            return self._mock_processing(file_path)
        
        processor = self.supported_extensions[ext]
        return processor(file_path)
    
    def _process_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Split into chunks (simple approach: split by paragraphs)
            chunks = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            return [
                {
                    "text": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk_id": i
                    }
                }
                for i, chunk in enumerate(chunks)
            ]
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            return self._mock_processing(file_path)
    
    def _process_markdown(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a markdown file"""
        # For demo mode, we'll just treat it like a text file
        return self._process_text(file_path)
    
    def _process_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract text content from the JSON (simplified approach)
            chunks = []
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > 10:
                        chunks.append(f"{key}: {value}")
            
            return [
                {
                    "text": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk_id": i
                    }
                }
                for i, chunk in enumerate(chunks)
            ]
        except Exception as e:
            logger.error(f"Error processing JSON file {file_path}: {e}")
            return self._mock_processing(file_path)
    
    def _process_html(self, file_path: str) -> List[Dict[str, Any]]:
        """Process an HTML file"""
        # For demo mode, we'll return a mock result
        return self._mock_processing(file_path)
    
    def _mock_pdf_processing(self, file_path: str) -> List[Dict[str, Any]]:
        """Mock PDF processing"""
        return self._mock_processing(file_path)
    
    def _mock_doc_processing(self, file_path: str) -> List[Dict[str, Any]]:
        """Mock Word document processing"""
        return self._mock_processing(file_path)
    
    def _mock_processing(self, file_path: str) -> List[Dict[str, Any]]:
        """Generate mock processing results for demo mode"""
        file_name = os.path.basename(file_path)
        
        # Create some realistic-looking chunks based on the filename
        mock_chunks = [
            f"This is a sample extracted content from {file_name}. "
            f"In a production environment, this would contain actual content from the document.",
            
            f"Section 1: Introduction to {file_name.split('.')[0]}. "
            f"This document contains important information that would be properly extracted and chunked "
            f"in a production environment.",
            
            f"Section 2: Technical details. The document {file_name} provides specifications and "
            f"implementation guidelines that would be properly parsed in production.",
            
            f"Section 3: Conclusion. The {file_name.split('.')[0]} framework offers significant "
            f"advantages for SLA management and cloud service integration.",
        ]
        
        return [
            {
                "text": chunk,
                "metadata": {
                    "source": file_path,
                    "chunk_id": i,
                    "demo_mode": True
                }
            }
            for i, chunk in enumerate(mock_chunks)
        ]

# Factory function to get a document processor
def get_document_processor() -> SimpleDocumentProcessor:
    """Get a document processor instance
    
    In demo mode, this returns a SimpleDocumentProcessor.
    
    Returns:
        A document processor instance
    """
    logger.info("Using simple document processor (demo mode)")
    return SimpleDocumentProcessor()