#!/usr/bin/env python3
"""
Test script for consultation templates functionality.

This script will:
1. Get all available consultation templates
2. Get a specific template by ID
3. Test creating a new consultation session with a template
4. Test progressing through consultation stages
"""
import sys
import os
import json
import requests
from pathlib import Path

# Add parent directory to path
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
sys.path.append(str(backend_dir))

# Base URL for API
API_URL = "http://localhost:8000/api"

# Auth token
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTc1OTE1OTcxOX0.xnyQC26G75b9tF-EqD1-Ckv4CXQoQIv8ssbfpeiOC6Y"

# Headers for requests
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def print_json(data):
    """Print JSON data in a formatted way."""
    print(json.dumps(data, indent=2))

def get_all_templates():
    """Get all consultation templates."""
    print("\n=== Getting all consultation templates ===")
    
    # Try different endpoint paths to find the correct one
    endpoints = [
        "/templates",
    ]
    
    for endpoint in endpoints:
        url = API_URL + endpoint
        print(f"Trying endpoint: {url}")
        
        response = requests.get(url, headers=HEADERS)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} templates")
            
            # Display template IDs and names
            for i, template in enumerate(data):
                print(f"{i+1}. ID: {template.get('id')}, Name: {template.get('name')}")
            
            # Save the first template ID for later use
            if data:
                return data[0].get('id')
    
    return None

def get_template_by_id(template_id):
    """Get a specific consultation template by ID."""
    print(f"\n=== Getting template with ID: {template_id} ===")
    
    # First try to get all templates and filter by ID
    response = requests.get(API_URL + "/templates", headers=HEADERS)
    if response.status_code == 200:
        templates = response.json()
        for template in templates:
            if template.get('id') == template_id:
                print(f"Found template: {template.get('name')}")
                print(f"Template description: {template.get('description')}")
                print(f"Number of stages: {len(template.get('stages', []))}")
                return template
    
    print(f"Could not find template with ID: {template_id}")
    return None
    
    return None

def create_consultation_session(template_id):
    """Create a new consultation session using a template."""
    print(f"\n=== Creating a new consultation session with template ID: {template_id} ===")
    
    # First, try posting to the consultation chat endpoint with template_id
    url = API_URL + "/consultation/chat"
    payload = {
        "role": "user",
        "content": f"I'd like to start a consultation using this template"
    }
    
    params = {"template_id": template_id}
    
    print(f"Sending POST to: {url}")
    print(f"Payload: {json.dumps(payload)}")
    print(f"Params: {json.dumps(params)}")
    
    response = requests.post(url, headers=HEADERS, json=payload, params=params)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if "session_id" in data:
            return data.get("session_id")
    
    print("Failed to create consultation session with template")
    return None

def continue_consultation(session_id, message):
    """Continue a consultation session by sending a message."""
    print(f"\n=== Continuing consultation session {session_id} ===")
    
    url = API_URL + "/consultation/chat"
    params = {"session_id": session_id}
    payload = {
        "role": "user",
        "content": message
    }
    
    print(f"Sending POST to: {url} with session_id={session_id}")
    print(f"Message: {message}")
    
    response = requests.post(url, headers=HEADERS, json=payload, params=params)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"AI response: {data.get('message')[:100]}...")
        
        # Check if we have template progress information
        if "template_progress" in data:
            progress = data["template_progress"]
            print(f"\nTemplate Progress:")
            print(f"- Completed stage: {progress.get('completed_stage')}")
            print(f"- Progress: {progress.get('progress_percentage')}%")
            
            if "next_stage" in progress:
                next_stage = progress["next_stage"]
                print(f"- Next stage: {next_stage.get('name')} ({next_stage.get('type')})")
                print(f"- Description: {next_stage.get('description')}")
            elif progress.get('status') == "completed":
                print(f"- Status: COMPLETED")
        
        return data
    
    print("Failed to continue consultation")
    return None

def main():
    """Main function to run the tests."""
    print("=== Starting Consultation Templates Test ===")
    
    # Get all templates
    template_id = get_all_templates()
    if not template_id:
        print("No templates found")
        return
    
    # Get specific template
    template = get_template_by_id(template_id)
    if not template:
        print(f"Failed to get template with ID: {template_id}")
        return
    
    # Create a consultation session
    session_id = create_consultation_session(template_id)
    if not session_id:
        print("Failed to create consultation session")
        return
    
    # Continue the consultation with sample responses
    stages = template.get("stages", [])
    if stages:
        # Send a message for each stage (simple test)
        for i, stage in enumerate(stages[:2]):  # Just test the first 2 stages
            print(f"\n--- Stage {i+1}: {stage.get('name')} ---")
            
            # Send a sample response based on the stage type
            stage_type = stage.get("stage_type")
            
            if stage_type == "information_gathering":
                message = "Here is the information you requested: headache, started yesterday, severity 7/10."
            elif stage_type == "problem_analysis":
                message = "Yes, I've tried taking pain medication but it hasn't helped much."
            elif stage_type == "recommendation":
                message = "Those recommendations sound good, I'll try them."
            elif stage_type == "summary":
                message = "Thanks for the summary."
            else:
                message = "I understand, please continue with the consultation."
            
            response = continue_consultation(session_id, message)
            if not response:
                print(f"Failed to continue consultation at stage {i+1}")
                break

if __name__ == "__main__":
    main()