# Healthcare RAG System Documentation

## Overview

The Healthcare RAG (Retrieval Augmented Generation) system enhances the Chakra SLA platform by providing source-backed recommendations for healthcare-specific requirements. The system retrieves relevant information from healthcare SLA documents and includes citations in the generated responses.

## Technical Implementation

### Components

1. **Document Indexing**
   - Uses ChromaDB as the vector store for document embeddings
   - Implements SentenceTransformer for generating embeddings
   - Documents are processed into chunks with metadata for source attribution

2. **Query Processing**
   - Healthcare-specific queries trigger the RAG system
   - Relevant chunks are retrieved based on semantic similarity
   - Retrieved information is included in the prompt to the LLM
   - Source information is returned alongside the generated response

3. **Frontend Integration**
   - Source citations are displayed in the UI through the chat component
   - Citations include document title, section, and page number when available

## Optimization Features

### Memory Usage Optimization

The RAG initialization process has been optimized to prevent system hangs:

1. **Batch Processing**
   - Documents are processed in small batches (configurable)
   - Each batch is processed and then added to the vector store
   - Prevents memory spikes during processing of large document collections

2. **Memory Monitoring**
   - System actively monitors memory usage during initialization
   - Can automatically stop if memory usage exceeds a configurable threshold
   - Prevents system crashes on resource-constrained environments

3. **Lightweight Mode**
   - Special mode for resource-constrained systems
   - Uses smaller batch sizes and stricter memory limits
   - Reduces model size when possible
   - Recommended for development environments and laptops

## Usage

### Starting the RAG System

The RAG system is automatically initialized when starting the Chakra application:

```bash
# Start Chakra with RAG initialization
./start_chakra.sh
```

The default configuration uses lightweight mode to prevent resource issues.

### Manual Initialization

You can manually initialize or update the RAG system:

```bash
# Standard initialization
python ./scripts/init_rag_system.py

# Lightweight mode (for resource-constrained systems)
python ./scripts/init_rag_system.py --lightweight
```

### Testing

Two test scripts are provided:

1. **Performance Testing**
   ```bash
   ./test_rag_performance.sh
   ```
   Tests the performance and memory usage of the RAG initialization process

2. **End-to-End Testing**
   ```bash
   ./test_rag_e2e.sh
   ```
   Tests the complete RAG system, including initialization and query functionality

## Troubleshooting

### System Hanging During Initialization

If the system hangs during initialization:

1. Try using lightweight mode:
   ```bash
   python ./scripts/init_rag_system.py --lightweight
   ```

2. Increase your system's available memory (close other applications)

3. Adjust batch size and memory threshold in `scripts/init_rag_system.py`:
   ```python
   # For very constrained systems
   BATCH_SIZE = 5  # Process fewer documents at once
   MAX_MEMORY_PERCENT = 70  # Stop at lower memory threshold
   ```

### Missing Sources in Responses

If sources are not appearing in responses:

1. Verify that the RAG system is properly initialized:
   ```bash
   python ./scripts/init_rag_system.py --debug
   ```

2. Check that industry is set to "Healthcare" in the consultation

3. Ensure the query is relevant to healthcare SLA content

## Future Improvements

- Support for additional industries and document types
- More granular source attribution (paragraph-level)
- Adaptive resource usage based on system capabilities
- Integration with more LLM providers