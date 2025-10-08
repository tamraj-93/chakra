#!/usr/bin/env python3
"""
Script to update the database schema with the new template models.
"""
import sys
import os
from pathlib import Path
from sqlalchemy import inspect, text
from datetime import datetime

# Add the parent directory to sys.path to allow importing from app
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
sys.path.append(str(backend_dir))

from app.core.database import SessionLocal, engine, Base
from app.models.database import User, SLATemplate, SLAMetric, ConsultationSession, Message, TokenUsage
from app.models.database_templates import (
    ConsultationTemplate, ConsultationStage, ExpectedOutput, Tag, template_tags
)


def update_schema():
    """Update the database schema with the new models."""
    print("Creating tables for new models...")
    
    # Create tables for new models
    inspector = inspect(engine)
    
    # Check if tables exist and create only those that don't
    tables_to_create = []
    for table in [
        ConsultationTemplate.__table__,
        ConsultationStage.__table__,
        ExpectedOutput.__table__,
        Tag.__table__,
        template_tags
    ]:
        if not inspector.has_table(table.name):
            tables_to_create.append(table)
            print(f"Will create table: {table.name}")
        else:
            print(f"Table {table.name} already exists, skipping")
    
    if tables_to_create:
        Base.metadata.create_all(bind=engine, tables=tables_to_create)
    
    # Now check if we need to add columns to consultation_sessions
    session = SessionLocal()
    try:
        # Check for template_id column
        has_template_id = False
        has_session_state = False
        has_updated_at = False
        
        for column in inspector.get_columns('consultation_sessions'):
            if column['name'] == 'template_id':
                has_template_id = True
                print("Column 'template_id' already exists in consultation_sessions")
            elif column['name'] == 'session_state':
                has_session_state = True
                print("Column 'session_state' already exists in consultation_sessions")
            elif column['name'] == 'updated_at':
                has_updated_at = True
                print("Column 'updated_at' already exists in consultation_sessions")
        
        # Add missing columns if needed
        if not (has_template_id and has_session_state and has_updated_at):
            connection = engine.connect()
            
            try:
                if not has_template_id:
                    print("Adding 'template_id' column to consultation_sessions")
                    connection.execute(text(
                        "ALTER TABLE consultation_sessions ADD COLUMN template_id VARCHAR"
                    ))
                
                if not has_session_state:
                    print("Adding 'session_state' column to consultation_sessions")
                    connection.execute(text(
                        "ALTER TABLE consultation_sessions ADD COLUMN session_state JSON"
                    ))
                
                if not has_updated_at:
                    print("Adding 'updated_at' column to consultation_sessions")
                    # SQLite doesn't support adding columns with DEFAULT expressions
                    connection.execute(text(
                        "ALTER TABLE consultation_sessions ADD COLUMN updated_at TIMESTAMP"
                    ))
                
                connection.commit()
            except Exception as e:
                connection.rollback()
                print(f"Error adding columns: {e}")
            finally:
                connection.close()
    
    finally:
        session.close()
    
    print("Schema update complete.")


if __name__ == "__main__":
    update_schema()