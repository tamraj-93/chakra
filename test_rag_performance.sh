#!/bin/bash

# Test script for RAG performance with different options
echo "Testing RAG system performance..."

# Define Python command based on environment
if [ -d "./backend/.venv" ]; then
    PYTHON_CMD="./backend/.venv/bin/python"
else
    PYTHON_CMD="python"
fi

# Test with lightweight mode
echo "Testing RAG initialization with lightweight mode..."
time $PYTHON_CMD ./scripts/init_rag_system.py --lightweight
echo "✓ Lightweight mode test completed"

# Test memory usage during initialization
echo "Monitoring memory usage during RAG initialization..."
$PYTHON_CMD -c "
import psutil
import subprocess
import time
import os

print('Starting memory monitoring...')
process = subprocess.Popen(['$PYTHON_CMD', './scripts/init_rag_system.py', '--lightweight'])

# Monitor memory usage
max_memory = 0
while process.poll() is None:
    memory_info = psutil.Process(process.pid).memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    max_memory = max(max_memory, memory_mb)
    print(f'Current memory usage: {memory_mb:.2f} MB')
    time.sleep(1)

print(f'Peak memory usage: {max_memory:.2f} MB')
"

echo "All tests completed!"