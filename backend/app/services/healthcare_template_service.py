"""
Service to load healthcare templates from files.
"""
import os
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class HealthcareTemplateService:
    """Service to manage healthcare templates from file system"""
    
    def __init__(self, templates_dir: str = None):
        """Initialize the healthcare template service"""
        if templates_dir is None:
            # Use the absolute path to the data/templates directory
            base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            self.templates_dir = os.path.join(base_dir, "data", "templates")
            print(f"Initialized with templates directory: {self.templates_dir}")
        else:
            self.templates_dir = templates_dir
    
    def get_healthcare_templates(self) -> List[Dict[str, Any]]:
        """Get all healthcare templates from the templates directory"""
        templates = []
        
        try:
            # Ensure the directory exists
            if not os.path.exists(self.templates_dir):
                logger.warning(f"Templates directory does not exist: {self.templates_dir}")
                return templates
            
            # Debug print
            print(f"Looking for templates in: {self.templates_dir}")
            print(f"Directory contents: {os.listdir(self.templates_dir)}")
            
            # List all JSON files in the directory
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.templates_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            template_data = json.load(f)
                        
                        # Check if this is a healthcare template
                        tags = template_data.get('tags', [])
                        domain = template_data.get('domain', '').lower()
                        
                        # Debug print
                        print(f"Template {filename}: tags={tags}, domain={domain}")
                        
                        if 'healthcare' in tags or 'healthcare' in domain.lower():
                            # Create template metadata
                            print(f"Found healthcare template: {filename}")
                            template = {
                                'id': template_data.get('id', os.path.splitext(filename)[0]),
                                'name': template_data.get('name', 'Unnamed Template'),
                                'description': template_data.get('description', ''),
                                'domain': domain,
                                'tags': tags,
                                'filename': filename,
                                'file_path': filepath
                            }
                            templates.append(template)
                    except Exception as e:
                        logger.error(f"Error loading template {filename}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
        
        return templates
    
    def get_template_by_id(self, template_id: str) -> Dict[str, Any]:
        """Get a specific healthcare template by ID"""
        try:
            logger = logging.getLogger(__name__)
            logger.info(f"Looking for template with ID: {template_id}")
            logger.info(f"Templates directory: {self.templates_dir}")
            
            # Check if the ID is a filename
            if template_id.endswith('.json'):
                filepath = os.path.join(self.templates_dir, template_id)
            else:
                filepath = os.path.join(self.templates_dir, f"{template_id}.json")
            
            logger.info(f"Checking for template at: {filepath}")
            
            if not os.path.exists(filepath):
                # Try with alternate extensions
                alt_filepath = os.path.join(self.templates_dir, f"{template_id}")
                logger.info(f"Template not found, trying alternate path: {alt_filepath}")
                
                if not os.path.exists(alt_filepath):
                    logger.warning(f"Template not found: {template_id}")
                    # List available templates for debugging
                    if os.path.exists(self.templates_dir):
                        logger.info(f"Available templates: {os.listdir(self.templates_dir)}")
                    return None
                filepath = alt_filepath
            
            logger.info(f"Loading template from: {filepath}")
            with open(filepath, 'r') as f:
                template_data = json.load(f)
            
            # Add metadata
            template_data['file_path'] = filepath
            template_data['filename'] = os.path.basename(filepath)
            
            # Validate that essential fields exist
            for field in ['id', 'name', 'description']:
                if field not in template_data:
                    logger.warning(f"Template {template_id} missing required field: {field}")
                    template_data[field] = template_id if field == 'id' else 'Unknown'
            
            logger.info(f"Template loaded successfully: {template_data['name']}")
            return template_data
        
        except Exception as e:
            logger.error(f"Error loading template {template_id}: {str(e)}")
            return None