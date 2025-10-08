"""
Healthcare-optimized RAG system for SLA documents
"""

from typing import List, Dict, Any, Optional, Tuple
import os
from datetime import datetime
import re
import json

# This would use langchain and other dependencies in a real implementation
# For this hackathon prototype, we'll create a simplified version

class HealthcareRAGSystem:
    """
    Retrieval Augmented Generation system optimized for healthcare SLA documents
    """
    
    def __init__(self, document_dir: str):
        """Initialize the RAG system with the path to documents"""
        self.document_dir = document_dir
        self.document_store = []
        self.vector_store = {}
        self.healthcare_terms = self._load_healthcare_terms()
        self.initialized = False
    
    def initialize(self):
        """Initialize the system by loading and indexing documents"""
        self._load_documents()
        self._create_embeddings()
        self.initialized = True
        return {"status": "success", "documents_indexed": len(self.document_store)}
    
    def _load_documents(self):
        """Load documents from the document directory"""
        # In a real implementation, this would load and parse the actual files
        # For this prototype, we'll just load metadata
        
        try:
            # Check if metadata file exists (simulating a database)
            metadata_file = os.path.join(self.document_dir, "document_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    self.document_store = json.load(f)
            
            # Load any documents from the directory that aren't in metadata
            for filename in os.listdir(self.document_dir):
                if filename.endswith(('.md', '.txt', '.pdf')) and not filename.startswith('.'):
                    file_path = os.path.join(self.document_dir, filename)
                    
                    # Check if document is already in store
                    doc_id = None
                    for doc in self.document_store:
                        if doc.get('filename') == filename:
                            doc_id = doc.get('id')
                            break
                    
                    if not doc_id:
                        # Add new document to store
                        doc_id = f"doc_{len(self.document_store) + 1}"
                        
                        # In a real implementation, we would parse the document content
                        # For this prototype, we'll just use filename
                        document = {
                            "id": doc_id,
                            "filename": filename,
                            "title": os.path.splitext(filename)[0],
                            "upload_date": datetime.now().isoformat(),
                            "file_size": os.path.getsize(file_path),
                            "status": "processed",
                            "chunks": []  # Will be populated during indexing
                        }
                        self.document_store.append(document)
        
        except Exception as e:
            print(f"Error loading documents: {e}")
            return {"status": "error", "message": str(e)}
    
    def _create_embeddings(self):
        """Create embeddings for all documents in the store"""
        # In a real implementation, this would use a proper embedding model
        # For this prototype, we'll simulate the process
        
        for document in self.document_store:
            # Clear existing chunks
            document["chunks"] = []
            
            # Try to read the actual document
            try:
                file_path = os.path.join(self.document_dir, document["filename"])
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Split into chunks (simplified)
                    chunks = self._chunk_document(content, document["id"])
                    document["chunks"] = chunks
                    
                    # Create simulated embeddings for each chunk
                    for chunk in chunks:
                        chunk_id = chunk["id"]
                        self.vector_store[chunk_id] = self._simulate_embedding(chunk["text"])
                        
            except Exception as e:
                print(f"Error processing document {document['filename']}: {e}")
    
    def _chunk_document(self, content: str, doc_id: str) -> List[Dict[str, Any]]:
        """Split document into chunks optimized for healthcare content"""
        # In a real implementation, this would use more sophisticated chunking
        # For this prototype, we'll use simple paragraph-based chunking
        
        chunks = []
        
        # Split by sections (headers)
        sections = re.split(r'\n#{1,6} ', content)
        
        for i, section in enumerate(sections):
            if i == 0 and not section.strip():
                continue
                
            # Further split large sections into smaller chunks
            if len(section) > 1000:
                paragraphs = re.split(r'\n\n+', section)
                for j, para in enumerate(paragraphs):
                    if not para.strip():
                        continue
                    
                    chunk_id = f"{doc_id}_c{i}_{j}"
                    chunks.append({
                        "id": chunk_id,
                        "doc_id": doc_id,
                        "text": para,
                        "section_idx": i,
                        "para_idx": j
                    })
            else:
                chunk_id = f"{doc_id}_c{i}"
                chunks.append({
                    "id": chunk_id,
                    "doc_id": doc_id,
                    "text": section,
                    "section_idx": i,
                    "para_idx": 0
                })
        
        return chunks
    
    def _simulate_embedding(self, text: str) -> List[float]:
        """
        Create a simulated embedding vector for text
        In a real implementation, this would use a proper embedding model
        """
        # For this prototype, we'll return a simple hash-based vector
        # This is just for simulation purposes
        import hashlib
        
        # Create a deterministic but simplified "embedding"
        hash_obj = hashlib.md5(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Convert bytes to a list of 8 float values between -1 and 1
        return [(b / 128) - 1 for b in hash_bytes[:8]]
    
    def _load_healthcare_terms(self) -> Dict[str, List[str]]:
        """Load healthcare terminology for query enhancement"""
        # In a real implementation, this would load from a comprehensive medical terminology database
        # For this prototype, we'll use a simplified set of terms
        
        return {
            "HIPAA": ["health insurance portability and accountability act", "privacy rule", "security rule", "phi", "ephi"],
            "EHR": ["electronic health record", "electronic medical record", "emr", "health record", "medical record"],
            "PHI": ["protected health information", "patient data", "health data", "medical data", "patient information"],
            "telemedicine": ["telehealth", "virtual care", "remote care", "video visit", "virtual visit"],
            "uptime": ["availability", "system availability", "service availability", "downtime", "outage"],
            "security": ["data security", "encryption", "access control", "authentication", "authorization"],
            "compliance": ["regulatory compliance", "regulation", "requirement", "standard", "certification"]
        }
    
    def enhance_query(self, query: str) -> str:
        """Enhance the query with healthcare terminology"""
        enhanced_query = query
        
        # Check for healthcare terms and expand with synonyms
        for term, synonyms in self.healthcare_terms.items():
            if re.search(r'\b' + re.escape(term) + r'\b', query, re.IGNORECASE):
                # Add relevant synonyms to the query
                enhanced_terms = " OR ".join([f'"{s}"' for s in synonyms[:3]])
                enhanced_query = f"{enhanced_query} ({enhanced_terms})"
        
        return enhanced_query
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks based on the query
        Returns the top_k most relevant chunks with document reference information
        """
        if not self.initialized:
            self.initialize()
        
        # Enhance query with healthcare terminology
        enhanced_query = self.enhance_query(query)
        
        # In a real implementation, this would use vector similarity search
        # For this prototype, we'll use keyword matching as a simplified approach
        
        results = []
        query_terms = set(re.findall(r'\b\w+\b', enhanced_query.lower()))
        
        for doc in self.document_store:
            for chunk in doc.get("chunks", []):
                chunk_text = chunk["text"].lower()
                
                # Count matching terms
                match_score = 0
                for term in query_terms:
                    if term in chunk_text:
                        match_score += 1
                
                # Only include results with at least one matching term
                if match_score > 0:
                    # Add document metadata and relevance score
                    results.append({
                        "chunk_id": chunk["id"],
                        "doc_id": doc["id"],
                        "document_title": doc["title"],
                        "document_filename": doc["filename"],
                        "chunk_text": chunk["text"],
                        "relevance_score": match_score / len(query_terms)
                    })
        
        # Sort by relevance score and return top_k results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]
    
    def generate_with_citations(self, query: str, context_chunks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a response with citations using RAG
        
        Args:
            query: The user query
            context_chunks: Optional pre-retrieved context chunks
            
        Returns:
            Dict containing the response text and citations
        """
        # If context not provided, retrieve it
        if context_chunks is None:
            context_chunks = self.search(query)
        
        if not context_chunks:
            # No relevant context found
            return {
                "answer": "I don't have enough information to answer this healthcare SLA question accurately.",
                "citations": []
            }
        
        # In a real implementation, this would use an LLM to generate the answer
        # For this prototype, we'll simulate a response based on the chunks
        
        # Build a response by combining information from the chunks
        citations = []
        referenced_docs = set()
        context_text = ""
        
        for i, chunk in enumerate(context_chunks):
            if i < 3:  # Use top 3 chunks for context
                context_text += chunk["chunk_text"] + "\n\n"
            
            # Track the citation
            doc_id = chunk["doc_id"]
            if doc_id not in referenced_docs:
                referenced_docs.add(doc_id)
                citations.append({
                    "doc_id": doc_id,
                    "document_title": chunk["document_title"],
                    "document_filename": chunk["document_filename"],
                    "relevance_score": chunk["relevance_score"]
                })
        
        # Simulate answer generation
        sample_answers = {
            "HIPAA compliance": "Healthcare SLAs require strict HIPAA compliance measures, including encryption of PHI, access controls, audit logging, and breach notification procedures. Business Associate Agreements should also specify these requirements.",
            "uptime requirements": "Healthcare SLAs typically require higher availability than other industries, with 99.95% or higher uptime for critical clinical systems. Maintenance windows should be limited and scheduled during off-hours.",
            "disaster recovery": "Healthcare SLAs should specify Recovery Time Objectives (RTO) of 2-4 hours for critical systems and Recovery Point Objectives (RPO) of 15 minutes or less to minimize data loss.",
            "response time": "Healthcare SLAs should define response times for different transaction types, with critical clinical functions typically requiring sub-second response times (e.g., medication ordering < 1.5 seconds, chart access < 1 second)."
        }
        
        # Determine which sample answer is most relevant to the query
        answer_key = "HIPAA compliance"  # default
        for key in sample_answers:
            if any(term in query.lower() for term in key.split()):
                answer_key = key
                break
                
        answer = sample_answers[answer_key]
        
        return {
            "answer": answer,
            "citations": citations,
            "context_used": context_chunks[:3]  # Return the chunks used for generating the answer
        }