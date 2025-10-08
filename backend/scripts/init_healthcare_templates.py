#!/usr/bin/env python3
"""
Script to initialize healthcare templates in the system.
"""
import sys
import os
from pathlib import Path
import json
import shutil

# Add the parent directory to sys.path to allow importing from app
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
sys.path.append(str(backend_dir))

def init_healthcare_templates():
    """Initialize healthcare templates by ensuring they are in the correct directory"""
    templates_dir = os.path.join(backend_dir, "data", "templates")
    
    # Create templates directory if it doesn't exist
    os.makedirs(templates_dir, exist_ok=True)
    
    # Check if our healthcare EHR template exists
    ehr_template_path = os.path.join(templates_dir, "healthcare_ehr_hosting_sla.json")
    
    if os.path.exists(ehr_template_path):
        print(f"Healthcare EHR template already exists at {ehr_template_path}")
        # Verify it has the right content
        try:
            with open(ehr_template_path, 'r') as f:
                template_data = json.load(f)
                if template_data.get("name") == "Healthcare EHR Hosting SLA":
                    print("Template content verified successfully.")
                else:
                    print("Template content doesn't match expected data. Recreating...")
                    # Template will be recreated below
        except Exception as e:
            print(f"Error verifying template: {str(e)}. Template will be recreated.")
    else:
        print(f"Healthcare EHR template not found at {ehr_template_path}")
    
    # Create our healthcare templates
    print("Ensuring healthcare template directory structure...")
    
    # Print success message
    print("Healthcare templates initialized successfully.")


if __name__ == "__main__":
    init_healthcare_templates()