#!/bin/bash

# Memory-Optimized RAG Initialization Script
# This script ensures proper memory management during RAG system initialization

# Set the base directory to the script's location
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Display header
echo "==========================================="
echo "   MEMORY-OPTIMIZED RAG INITIALIZATION"
echo "==========================================="

# Determine Python command
PYTHON_CMD="python3"
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD="python"
    if ! command -v $PYTHON_CMD &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        exit 1
    fi
fi

# Determine memory availability
echo "Checking system memory..."
FREE_MEM_PERCENT=30

# On Linux, use free command to get memory info
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
    FREE_MEM=$(free -m | awk '/^Mem:/{print $4}')
    FREE_PERCENT=$((FREE_MEM * 100 / TOTAL_MEM))
    
    echo "Memory stats: ${FREE_MEM}MB free out of ${TOTAL_MEM}MB total (${FREE_PERCENT}% free)"
    
    if [ $TOTAL_MEM -lt 4000 ]; then
        echo "Low memory system detected - using ultra-conservative settings"
        FREE_MEM_PERCENT=20
        LIGHTWEIGHT="--lightweight --max-memory 20"
    elif [ $TOTAL_MEM -lt 8000 ]; then
        echo "Medium-low memory system detected - using conservative settings"
        FREE_MEM_PERCENT=30
        LIGHTWEIGHT="--lightweight --max-memory 30"
    elif [ $TOTAL_MEM -lt 16000 ]; then
        echo "Medium memory system detected - using moderate settings"
        FREE_MEM_PERCENT=45
        LIGHTWEIGHT="--lightweight --max-memory 45"
    else
        echo "High memory system detected - using standard settings"
        FREE_MEM_PERCENT=60
        LIGHTWEIGHT="--max-memory 60"
    fi
else
    # Default to conservative settings if we can't determine memory
    echo "Cannot determine system memory - using conservative settings"
    LIGHTWEIGHT="--lightweight --max-memory 30"
fi

# Check if virtual environment exists, activate it
cd "$BASE_DIR/backend"
if [ -d ".venv" ]; then
    echo "Activating Python virtual environment..."
    source .venv/bin/activate
fi

# Check for psutil
echo "Checking for psutil..."
$PYTHON_CMD -c "import psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing psutil for memory monitoring..."
    $PYTHON_CMD -m pip install psutil
fi

# Clean up memory before starting
echo "Cleaning system memory cache..."
if command -v sync &> /dev/null; then
    sync
    if [ -w "/proc/sys/vm/drop_caches" ]; then
        echo "Dropping filesystem caches..."
        echo 1 > /proc/sys/vm/drop_caches
    fi
fi

# Close unnecessary applications (optional message)
echo "For best results, please close other memory-intensive applications"
echo "before continuing."
echo -n "Press Enter to continue with RAG initialization..."
read

# Run RAG initialization with the determined settings
echo -e "\nInitializing RAG system with optimized memory settings..."
echo "Command: $PYTHON_CMD ./scripts/init_rag_system.py $LIGHTWEIGHT"
$PYTHON_CMD ./scripts/init_rag_system.py $LIGHTWEIGHT

# Check the result
if [ $? -eq 0 ]; then
    echo -e "\n✅ RAG system initialized successfully!"
else
    echo -e "\n⚠️ RAG initialization encountered issues."
    echo "You may need to run with more conservative memory settings:"
    echo "$PYTHON_CMD ./scripts/init_rag_system.py --lightweight --max-memory 15"
fi

echo -e "\nRAG initialization complete. You can now start the application."