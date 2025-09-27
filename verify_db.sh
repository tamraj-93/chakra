#!/bin/bash

# Script to verify database initialization for the Chakra application

# Set colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}====================================${NC}"
echo -e "${YELLOW}   CHAKRA DATABASE VERIFICATION    ${NC}"
echo -e "${YELLOW}====================================${NC}"

# Set the base directory to the script's location
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR/backend"

# Check for Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 is not installed. Please install Python 3.8 or newer.${NC}"
    exit 1
fi

# Check if virtual environment exists, if not activate it
if [ ! -d ".venv" ]; then
    echo -e "${RED}Virtual environment not found. Please run ./init_db.sh first.${NC}"
    exit 1
else
    source .venv/bin/activate
fi

# Create a temporary verification script
cat << 'EOF' > verify_db.py
#!/usr/bin/env python3
"""
Script to verify the database initialization for the Chakra application.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.database import User, SLAMetric, SLATemplate, ConsultationSession, Message

def verify_database():
    """Verify database initialization."""
    db = SessionLocal()
    
    try:
        # Check users
        users = db.query(User).all()
        user_count = len(users)
        print(f"✓ Found {user_count} users in the database")
        
        if user_count > 0:
            for user in users:
                print(f"  - User: {user.email} (ID: {user.id})")
                
        # Check SLA metrics
        metrics = db.query(SLAMetric).all()
        metric_count = len(metrics)
        print(f"✓ Found {metric_count} SLA metrics in the database")
        
        if metric_count > 0:
            for metric in metrics[:3]:  # Show only first 3 for brevity
                print(f"  - Metric: {metric.name} ({metric.category})")
            if metric_count > 3:
                print(f"  - ... and {metric_count - 3} more")
                
        # Check SLA templates
        templates = db.query(SLATemplate).all()
        template_count = len(templates)
        print(f"✓ Found {template_count} SLA templates in the database")
        
        if template_count > 0:
            for template in templates:
                print(f"  - Template: {template.name} (Owner: {template.user_id})")
                
        # Check consultation sessions
        sessions = db.query(ConsultationSession).all()
        session_count = len(sessions)
        print(f"✓ Found {session_count} consultation sessions in the database")
        
        if session_count > 0:
            for session in sessions:
                message_count = db.query(Message).filter(Message.session_id == session.id).count()
                print(f"  - Session: {session.session_type} (User: {session.user_id}, Messages: {message_count})")
                
        # Overall verification
        if user_count > 0 and metric_count > 0 and template_count > 0 and session_count > 0:
            print("\n✓ Database initialization verification PASSED!")
            return True
        else:
            print("\n✗ Database initialization incomplete. Some tables are empty.")
            return False
            
    finally:
        db.close()

if __name__ == "__main__":
    success = verify_database()
    sys.exit(0 if success else 1)
EOF

# Make the verification script executable
chmod +x verify_db.py

echo -e "\n${YELLOW}Verifying database initialization...${NC}"
python3 verify_db.py

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Database verification complete! Your database is properly initialized.${NC}"
    echo -e "${GREEN}You can now run the application with: ./start_chakra.sh${NC}"
else
    echo -e "\n${RED}Database verification failed! Please run ./init_db.sh to initialize the database.${NC}"
fi

# Clean up the temporary script
rm verify_db.py

echo -e "\n${YELLOW}====================================${NC}"