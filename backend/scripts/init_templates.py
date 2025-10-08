#!/usr/bin/env python3
"""
Script to initialize consultation templates in the database.
"""
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to allow importing from app
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
sys.path.append(str(backend_dir))

from app.core.database import SessionLocal, engine, Base
from app.models.database_templates import ConsultationTemplate, ConsultationStage, ExpectedOutput, Tag
from app.services.sample_templates import (
    HEALTH_CONSULTATION,
    TECH_SUPPORT_CONSULTATION,
    FINANCIAL_ADVISORY_CONSULTATION
)
import uuid


def create_template(db, template_data, user_id=None):
    """Create a consultation template in the database."""
    # Create the template
    db_template = ConsultationTemplate(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=template_data["name"],
        description=template_data["description"],
        domain=template_data["domain"],
        version=template_data["version"],
        initial_system_prompt=template_data["initial_system_prompt"],
        is_public=True  # Make sample templates public
    )
    
    db.add(db_template)
    db.flush()  # Flush to get the template ID
    
    # Process tags
    for tag_name in template_data["tags"]:
        # Check if tag exists, if not create it
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.flush()
        
        db_template.tags.append(tag)
    
    # Create stages
    for i, stage in enumerate(template_data["stages"]):
        db_stage = ConsultationStage(
            id=str(uuid.uuid4()),
            template_id=db_template.id,
            name=stage["name"],
            description=stage["description"],
            stage_type=stage["stage_type"],
            prompt_template=stage["prompt_template"],
            system_instructions=stage["system_instructions"],
            ui_components=stage["ui_components"],
            next_stage_conditions=stage["next_stage_conditions"],
            sequence_order=i
        )
        
        db.add(db_stage)
        db.flush()  # Flush to get the stage ID
        
        # Create expected outputs
        for output in stage["expected_outputs"]:
            db_output = ExpectedOutput(
                stage_id=db_stage.id,
                name=output["name"],
                description=output["description"],
                data_type=output["data_type"],
                required=output.get("required", True)
            )
            
            db.add(db_output)
    
    return db_template


def init_templates():
    """Initialize consultation templates in the database."""
    db = SessionLocal()
    try:
        # Check if templates already exist
        existing_count = db.query(ConsultationTemplate).count()
        if existing_count > 0:
            print(f"Found {existing_count} existing templates. Skipping initialization.")
            return
        
        # Create sample templates
        templates = [
            ("Health Consultation", HEALTH_CONSULTATION),
            ("Tech Support", TECH_SUPPORT_CONSULTATION),
            ("Financial Advisory", FINANCIAL_ADVISORY_CONSULTATION)
        ]
        
        for name, data in templates:
            print(f"Creating {name} template...")
            create_template(db, data)
        
        db.commit()
        print("Templates initialized successfully.")
    
    except Exception as e:
        db.rollback()
        print(f"Error initializing templates: {e}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    init_templates()