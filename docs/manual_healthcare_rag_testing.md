# Manual Healthcare RAG Testing Instructions

This document provides step-by-step instructions for testing the Healthcare RAG (Retrieval Augmented Generation) functionality in the Chakra system.

## Prerequisites

- Python 3.x installed
- Terminal/command-line access
- Chakra project files

## Step 1: Use the Existing Chakra Environment

The Chakra project already sets up a virtual environment in the `backend/.venv` directory when you run `start_chakra.sh`. We'll use this environment for our RAG testing.

First, make sure the RAG dependencies are added to your environment:

```bash
# Make the update script executable
chmod +x update_rag_dependencies.sh

# Run the update script
./update_rag_dependencies.sh
```

This script will:
- Find and activate the existing Chakra virtual environment
- Install the necessary RAG packages (chromadb, sentence-transformers, etc.)
- Prepare your environment for healthcare RAG testing

## Step 2: Run the Healthcare RAG Tests

After updating the dependencies, you can run the healthcare RAG tests:

```bash
# Make sure the test script is executable
chmod +x run_healthcare_rag_test.sh

# Run the healthcare RAG test script
./run_healthcare_rag_test.sh
```

This script will:
1. Detect and activate the Chakra virtual environment
2. Check for the required packages and offer to install any missing ones
3. Run the minimal test first to verify basic functionality
4. Run the full healthcare RAG tests

## Step 3: Run Individual Tests (Optional)

If you want to run specific tests manually:

```bash
# First activate the Chakra virtual environment
source backend/.venv/bin/activate

# Run the minimal test
cd backend
python scripts/minimal_test_healthcare_rag.py

# Or run a specific test script
python scripts/test_healthcare_rag.py

# Deactivate the environment when done
deactivate
```

## Step 4: Manual Testing with Python Shell

If you prefer more hands-on testing, you can use a Python shell:

```bash
cd /home/nilabh/Projects/chakra/backend
python3
```

Then in the Python shell:

```python
# Import required modules
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import chromadb
from sentence_transformers import SentenceTransformer

# Create a simple test vector store
client = chromadb.PersistentClient(path="data/manual_test_db")
embedding_fn = SentenceTransformer('all-MiniLM-L6-v2')

# Create a collection
collection = client.get_or_create_collection(
    name="test_healthcare_collection",
    embedding_function=lambda texts: embedding_fn.encode(texts).tolist()
)

# Add test healthcare documents
collection.add(
    documents=[
        "Healthcare SLA - Uptime: 99.99% guaranteed for healthcare applications. All systems must comply with HIPAA regulations.",
        "Patient data must be encrypted at rest with AES-256 encryption. All PHI transmissions require TLS 1.2 or higher.",
        "Telemedicine platform must support HD video (720p) quality with 25fps minimum frame rate. Audio-video sync within 50ms."
    ],
    ids=["doc1", "doc2", "doc3"]
)

# Test a query
results = collection.query(
    query_texts=["What are the security requirements for patient data?"],
    n_results=2
)

# Print results
print("\nResults:")
for doc, distance in zip(results["documents"][0], results["distances"][0]):
    similarity = 1 - min(distance, 1.0)
    print(f"Similarity: {similarity:.2f}")
    print(f"Document: {doc}\n")
```

## Step 5: Visualize Results (If Available)

If you've run the full tests and want to visualize results:

```bash
cd /home/nilabh/Projects/chakra
python3 visualize_healthcare_rag_results.py
```

## Troubleshooting

1. **ImportError: No module named 'pip'**
   - Run `./install_dependencies.sh` to install pip

2. **ModuleNotFoundError: No module named 'chromadb'**
   - Run `./install_dependencies.sh` to install missing packages
   - Or manually install: `python3 -m pip install --user chromadb sentence-transformers`

3. **Permission denied when running scripts**
   - Make scripts executable: `chmod +x script_name.sh`

4. **Python version issues**
   - Make sure you're using Python 3: `python3 --version`
   - Update your scripts to use `python3` instead of `python`

## Additional Notes

- The RAG system is designed to retrieve relevant SLA documents based on healthcare-related queries
- Adjust the embedding model if needed for better domain-specific results
- For production use, more comprehensive healthcare documents should be added to the vector store