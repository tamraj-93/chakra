#!/bin/bash
# Test script to check if healthcare templates are properly loaded in the Docker container

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

echo_color "blue" "=== Testing Healthcare Templates in Docker Container ==="
echo_color "blue" "Checking if container is running..."

if docker ps | grep -q chakra-backend-demo; then
    echo_color "green" "✅ Container is running"
else
    echo_color "red" "❌ Container is not running! Please start it first."
    exit 1
fi

echo_color "blue" "Checking templates directory..."
if docker exec chakra-backend-demo ls -la /app/backend/data/templates > /dev/null 2>&1; then
    echo_color "green" "✅ Templates directory exists"
    docker exec chakra-backend-demo ls -la /app/backend/data/templates
else
    echo_color "red" "❌ Templates directory does not exist in the container"
    echo_color "yellow" "Creating templates directory..."
    docker exec chakra-backend-demo mkdir -p /app/backend/data/templates
    echo_color "green" "✅ Templates directory created"
fi

echo_color "blue" "Checking for healthcare templates..."
if docker exec chakra-backend-demo ls -la /app/backend/data/templates | grep -q healthcare; then
    echo_color "green" "✅ Healthcare template files found:"
    docker exec chakra-backend-demo ls -la /app/backend/data/templates | grep healthcare
else
    echo_color "yellow" "⚠️ No healthcare templates found. Creating sample templates..."
    
    # Create a sample healthcare template
    echo_color "blue" "Creating sample healthcare template..."
    cat > healthcare_ehr_hosting_sla.json << 'EOF'
{
  "id": "healthcare-ehr-hosting-sla",
  "name": "Healthcare EHR Hosting SLA",
  "description": "A template to guide healthcare providers through creating SLAs for EHR hosting services",
  "domain": "Healthcare",
  "version": "1.0",
  "tags": ["healthcare", "EHR", "cloud hosting", "HIPAA", "medical data"],
  "initial_system_prompt": "You are Chakra, an AI assistant specializing in healthcare SLAs. Your goal is to help healthcare providers create comprehensive service level agreements for Electronic Health Record (EHR) hosting services."
}
EOF
    docker cp healthcare_ehr_hosting_sla.json chakra-backend-demo:/app/backend/data/templates/
    rm healthcare_ehr_hosting_sla.json
    echo_color "green" "✅ Sample healthcare template created and copied to container"
fi

echo_color "blue" "Testing API endpoint for healthcare templates..."
echo_color "blue" "Response from API:"
curl -s http://localhost:8000/api/healthcare-templates

echo ""
echo_color "yellow" "If you don't see any templates above, the API might need to be patched."
echo_color "blue" "Would you like to add the healthcare templates API endpoint to the demo API? (y/n)"
read answer

if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
    echo_color "blue" "Creating helper function to load templates..."
    cat > get_healthcare_templates.py << 'EOF'
import json
import os

def get_healthcare_templates():
    """Get all healthcare templates from the templates directory"""
    templates = []
    templates_dir = "/app/backend/data/templates"
    
    # List all JSON files in the directory
    if os.path.exists(templates_dir):
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(templates_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        template_data = json.load(f)
                    
                    # Create template metadata
                    template = {
                        'id': template_data.get('id', os.path.splitext(filename)[0]),
                        'name': template_data.get('name', 'Unnamed Template'),
                        'description': template_data.get('description', ''),
                        'domain': template_data.get('domain', ''),
                        'tags': template_data.get('tags', []),
                        'filename': filename
                    }
                    templates.append(template)
                except Exception as e:
                    print(f"Error loading template {filename}: {str(e)}")
    else:
        print(f"Templates directory does not exist: {templates_dir}")
    
    return templates
EOF
    docker cp get_healthcare_templates.py chakra-backend-demo:/app/
    rm get_healthcare_templates.py
    
    echo_color "blue" "Creating patch for demo_main.py..."
    cat > patch_main.py << 'EOF'
# Patch for healthcare templates
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import sys, os

# Insert healthcare templates code
sys.path.append('/app')
from get_healthcare_templates import get_healthcare_templates

# Add healthcare templates endpoints
@app.get("/api/healthcare-templates")
@app.get("/api/v1/healthcare-templates")
async def healthcare_templates_endpoint():
    """Get all healthcare templates"""
    templates = get_healthcare_templates()
    return templates

@app.get("/api/healthcare-templates/{template_id}")
@app.get("/api/v1/healthcare-templates/{template_id}")
async def healthcare_template_by_id(template_id: str):
    """Get a specific healthcare template by ID"""
    templates = get_healthcare_templates()
    for template in templates:
        if template['id'] == template_id:
            return template
    raise HTTPException(status_code=404, detail=f"Healthcare template not found: {template_id}")

logger.info("Healthcare template endpoints added")
EOF
    docker cp patch_main.py chakra-backend-demo:/app/
    rm patch_main.py
    
    echo_color "blue" "Patching demo_main.py..."
    docker exec chakra-backend-demo bash -c "cat /app/patch_main.py >> /app/demo_main.py"
    
    echo_color "blue" "Restarting the container..."
    docker restart chakra-backend-demo
    
    echo_color "yellow" "Waiting for container to restart..."
    sleep 5
    
    echo_color "blue" "Testing API endpoint again:"
    curl -s http://localhost:8000/api/healthcare-templates
    echo ""
    
    echo_color "green" "✅ Done! Healthcare templates should now be accessible via the API."
    echo_color "yellow" "If you still don't see any templates, check the container logs:"
    echo_color "yellow" "docker logs chakra-backend-demo"
else
    echo_color "yellow" "Skipped patching the API."
fi

echo ""
echo_color "blue" "=== Test Complete ==="