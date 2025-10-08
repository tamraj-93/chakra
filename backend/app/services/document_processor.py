"""
Document Processing Service for RAG Implementation

This module provides functionality for:
- Loading SLA documents from various formats (PDF, DOCX, TXT)
- Processing and preparing documents for embedding
- Extracting metadata like industry, service type, etc.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import re

# Unstructured imports for document loading
from unstructured.partition.auto import partition
from unstructured.staging.base import convert_to_dict
from unstructured.documents.elements import Title, NarrativeText, Text, ListItem

# Set up logging
logger = logging.getLogger(__name__)

# Configure document directories
DEFAULT_DOCUMENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "documents")

class DocumentProcessor:
    """
    Service for loading and processing SLA documents for the RAG system.
    """
    
    def __init__(self, document_dir: str = DEFAULT_DOCUMENT_DIR):
        """
        Initialize the document processor.
        
        Args:
            document_dir: Directory containing SLA documents
        """
        self.document_dir = document_dir
        os.makedirs(document_dir, exist_ok=True)
        logger.info(f"Initialized document processor with directory: {document_dir}")
    
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load and process a single document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Document dictionary with content and metadata
        """
        logger.info(f"Loading document: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Partition the document
            elements = partition(filename=file_path)
            
            # Convert elements to text
            content = "\n\n".join([str(element) for element in elements])
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, content, elements)
            
            return {
                "content": content,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise
    
    def load_directory(self, dir_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load all documents from a directory.
        
        Args:
            dir_path: Directory path to load from, defaults to the configured document_dir
            
        Returns:
            List of document dictionaries
        """
        dir_path = dir_path or self.document_dir
        logger.info(f"Loading all documents from directory: {dir_path}")
        
        documents = []
        
        # Check if directory exists
        if not os.path.exists(dir_path):
            logger.warning(f"Directory not found: {dir_path}")
            return documents
        
        # Get all files with supported extensions
        supported_extensions = ['.pdf', '.docx', '.txt', '.md', '.json']
        files = [
            os.path.join(dir_path, f) for f in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, f)) and 
            any(f.lower().endswith(ext) for ext in supported_extensions)
        ]
        
        # Process each file
        for file_path in files:
            try:
                doc = self.load_file(file_path)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                continue
        
        logger.info(f"Loaded {len(documents)} documents from {dir_path}")
        return documents
    
    def save_document(self, content: str, metadata: Dict[str, Any], file_name: Optional[str] = None) -> str:
        """
        Save a document to the document directory.
        
        Args:
            content: Document content
            metadata: Document metadata
            file_name: Optional file name, will be generated if not provided
            
        Returns:
            Path to the saved document
        """
        # Generate file name if not provided
        if file_name is None:
            industry = metadata.get('industry', 'general')
            service = metadata.get('service_type', 'service')
            file_name = f"sla_{industry}_{service}_{hex(hash(content))[-6:]}.json"
        
        # Ensure file has .json extension
        if not file_name.lower().endswith('.json'):
            file_name += '.json'
        
        file_path = os.path.join(self.document_dir, file_name)
        
        # Create the document dictionary
        document = {
            "content": content,
            "metadata": metadata
        }
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, indent=2)
        
        logger.info(f"Saved document to {file_path}")
        return file_path
    
    def _extract_metadata(self, file_path: str, content: str, elements: List[Any]) -> Dict[str, Any]:
        """
        Extract metadata from document content and file information.
        
        Args:
            file_path: Path to the document file
            content: Document content
            elements: Parsed document elements
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            "source": file_path,
            "filename": os.path.basename(file_path),
            "file_type": os.path.splitext(file_path)[1].lower().replace('.', ''),
        }
        
        # Extract document title from first title element if available
        for element in elements:
            if isinstance(element, Title):
                metadata["title"] = str(element)
                break
        
        # Try to extract industry information
        industry_patterns = [
            (r"healthcare|health\s*care|medical|hospital|clinical", "healthcare"),
            (r"financial|finance|banking|investment|insurance", "financial"),
            (r"retail|e-commerce|ecommerce|shop|commerce", "retail"),
            (r"telecom|telecommunications", "telecommunications"),
            (r"cloud|computing|it\s*service", "it_services"),
        ]
        
        for pattern, industry in industry_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                metadata["industry"] = industry
                break
        
        # Try to extract service type
        service_patterns = [
            (r"cloud\s*storage|storage\s*service", "cloud_storage"),
            (r"network|connectivity", "network"),
            (r"security|protection", "security"),
            (r"database|data\s*storage", "database"),
            (r"hosting|web\s*hosting", "hosting"),
            (r"api|application\s*interface", "api"),
        ]
        
        for pattern, service_type in service_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                metadata["service_type"] = service_type
                break
        
        # Try to extract compliance frameworks
        compliance_frameworks = []
        compliance_patterns = [
            (r"GDPR|General\s*Data\s*Protection\s*Regulation", "GDPR"),
            (r"HIPAA|Health\s*Insurance\s*Portability", "HIPAA"),
            (r"PCI\s*DSS|Payment\s*Card\s*Industry", "PCI-DSS"),
            (r"SOC\s*2|Service\s*Organization\s*Control", "SOC2"),
            (r"ISO\s*27001", "ISO27001"),
        ]
        
        for pattern, framework in compliance_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                compliance_frameworks.append(framework)
        
        if compliance_frameworks:
            metadata["compliance_frameworks"] = compliance_frameworks
        
        return metadata

# Helper function to get document processor instance
def get_document_processor() -> DocumentProcessor:
    """
    Get a document processor instance.
    
    Returns:
        DocumentProcessor instance
    """
    return DocumentProcessor()