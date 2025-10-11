#!/bin/bash
# Advanced health check script for Chakra backend

set -e

# Function for colored output
function echo_color() {
    local color=$1
    local message=$2
    
    case $color in
        "red") echo -e "\033[0;31m$message\033[0m" ;;
        "green") echo -e "\033[0;32m$message\033[0m" ;;
        "yellow") echo -e "\033[0;33m$message\033[0m" ;;
        "blue") echo -e "\033[0;34m$message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# API endpoint check
echo_color "blue" "Checking API health..."
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [[ "$API_HEALTH" == "200" ]]; then
    echo_color "green" "✅ API is healthy"
else
    echo_color "red" "❌ API health check failed with status code: $API_HEALTH"
    exit 1
fi

# Database connectivity check
echo_color "blue" "Checking database connectivity..."
DB_CHECK=$(curl -s http://localhost:8000/health | grep -o '"database":true' || echo "")

if [[ ! -z "$DB_CHECK" ]]; then
    echo_color "green" "✅ Database connection is healthy"
else
    echo_color "red" "❌ Database connection check failed"
    exit 1
fi

# Memory usage check
echo_color "blue" "Checking memory usage..."
MEMORY_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
MEMORY_THRESHOLD=90

if (( $(echo "$MEMORY_USAGE < $MEMORY_THRESHOLD" | bc -l) )); then
    echo_color "green" "✅ Memory usage is within acceptable range: ${MEMORY_USAGE}%"
else
    echo_color "yellow" "⚠️ High memory usage detected: ${MEMORY_USAGE}%"
    # Not failing health check for high memory, just warning
fi

# Disk space check
echo_color "blue" "Checking disk space..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
DISK_THRESHOLD=90

if (( $DISK_USAGE < $DISK_THRESHOLD )); then
    echo_color "green" "✅ Disk space usage is within acceptable range: ${DISK_USAGE}%"
else
    echo_color "yellow" "⚠️ High disk usage detected: ${DISK_USAGE}%"
    # Not failing health check for disk space, just warning
fi

# Ollama connectivity check (if not in demo mode)
if [[ "$DEMO_MODE" != "true" && "$LLM_PROVIDER" == "ollama" ]]; then
    echo_color "blue" "Checking Ollama connectivity..."
    OLLAMA_CHECK=$(curl -s -o /dev/null -w "%{http_code}" $OLLAMA_API_URL/api/health 2>/dev/null || echo "000")
    
    if [[ "$OLLAMA_CHECK" == "200" ]]; then
        echo_color "green" "✅ Ollama is accessible"
    else
        echo_color "yellow" "⚠️ Ollama check failed with status code: $OLLAMA_CHECK"
        # Not failing health check for Ollama in case it's temporarily down
    fi
fi

echo_color "green" "✅ All critical health checks passed!"
exit 0