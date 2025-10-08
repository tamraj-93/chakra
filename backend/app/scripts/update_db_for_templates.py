"""
Script to update database schema for template-based consultations.
This adds missing columns to existing tables if needed.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
import sys

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import SQLALCHEMY_DATABASE_URL

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_sql(engine, sql, message):
    """Run a SQL command and log the result."""
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        logger.info(f"✓ {message}")
        return True
    except SQLAlchemyError as e:
        if "duplicate column" in str(e).lower():
            logger.info(f"Column already exists: {str(e)}")
            return True
        logger.error(f"✗ {message} failed: {str(e)}")
        return False

def update_database_schema():
    """Update the database schema for template-based consultations."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Check if engine can connect to database
    try:
        with engine.connect() as conn:
            logger.info("Connected to database successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        return False
    
    # For SQLite, we need to check if columns exist first since it doesn't support IF NOT EXISTS
    # Check if template_id column exists in consultation_sessions
    try:
        # Try to add template_id column
        add_template_id_sql = """
        ALTER TABLE consultation_sessions 
        ADD COLUMN template_id VARCHAR;
        """
        run_sql(engine, add_template_id_sql, "Adding template_id column to consultation_sessions")
        logger.info("✓ Added template_id column")
    except SQLAlchemyError as e:
        if "duplicate column" in str(e).lower():
            logger.info("✓ template_id column already exists")
        else:
            logger.error(f"✗ Error adding template_id column: {str(e)}")
    
    # Check if session_state column exists
    try:
        # Try to add session_state column
        add_session_state_sql = """
        ALTER TABLE consultation_sessions 
        ADD COLUMN session_state JSON;
        """
        run_sql(engine, add_session_state_sql, "Adding session_state column to consultation_sessions")
        logger.info("✓ Added session_state column")
    except SQLAlchemyError as e:
        if "duplicate column" in str(e).lower():
            logger.info("✓ session_state column already exists")
        else:
            logger.error(f"✗ Error adding session_state column: {str(e)}")
    
    # Check if updated_at column exists
    try:
        # Try to add updated_at column
        add_updated_at_sql = """
        ALTER TABLE consultation_sessions 
        ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """
        run_sql(engine, add_updated_at_sql, "Adding updated_at column to consultation_sessions")
        logger.info("✓ Added updated_at column")
    except SQLAlchemyError as e:
        if "duplicate column" in str(e).lower():
            logger.info("✓ updated_at column already exists")
        else:
            logger.error(f"✗ Error adding updated_at column: {str(e)}")
    
    # Check if stage_id column exists
    try:
        # Try to add stage_id column
        add_stage_id_sql = """
        ALTER TABLE messages 
        ADD COLUMN stage_id VARCHAR;
        """
        run_sql(engine, add_stage_id_sql, "Adding stage_id column to messages")
        logger.info("✓ Added stage_id column")
    except SQLAlchemyError as e:
        if "duplicate column" in str(e).lower():
            logger.info("✓ stage_id column already exists")
        else:
            logger.error(f"✗ Error adding stage_id column: {str(e)}")
            
    return True
    
    logger.info("Database schema updated successfully")
    return True

if __name__ == "__main__":
    logger.info("Starting database schema update for template-based consultations...")
    success = update_database_schema()
    if success:
        logger.info("Schema update completed successfully")
    else:
        logger.error("Schema update failed")