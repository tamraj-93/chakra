#!/usr/bin/env python
"""
Script to initialize the database with sample consultations and messages.
This ensures we have sample data for testing consultations.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.models.consultation import ConsultationSession, Message
from app.services import user as user_service
import json
from datetime import datetime, timedelta

def init_consultations():
    """Initialize consultations and messages in the database."""
    # Create a session
    db = SessionLocal()
    
    try:
        # Check if we already have users
        user = user_service.get_user_by_email(db, email="user@example.com")
        
        if not user:
            print("User not found. Please run init_db.py first.")
            return
            
        # Check if we already have consultation sessions
        from sqlalchemy import inspect
        inspector = inspect(engine)
        if not 'consultation_sessions' in inspector.get_table_names():
            print("Creating consultation tables...")
            Base.metadata.create_all(bind=engine)
        
        # Create consultation sessions
        create_sample_consultations(db, user.id)
            
        print("Consultation initialization completed!")
        
    finally:
        db.close()

def create_sample_consultations(db: Session, user_id: int):
    """Create sample consultation sessions and messages."""
    # Check if we already have consultations for this user
    from app.models.database import ConsultationSession as DBConsultationSession
    
    existing = db.query(DBConsultationSession).filter(
        DBConsultationSession.user_id == user_id
    ).count()
    
    if existing > 0:
        print(f"User already has {existing} consultation sessions. Skipping.")
        return
        
    # Create a discovery session
    discovery_session = DBConsultationSession(
        user_id=user_id,
        session_type="discovery",
        context_data={
            "industry": "Healthcare",
            "service_type": "Telemedicine Platform",
            "key_concerns": ["HIPAA compliance", "Uptime guarantees", "Support response times"]
        },
        recommendations={}
    )
    
    db.add(discovery_session)
    db.flush()  # Get the ID without committing
    
    # Create messages for the discovery session
    discovery_messages = [
        {
            "content": "I need help creating an SLA for our telemedicine platform.",
            "role": "user",
            "timestamp": datetime.now() - timedelta(minutes=30)
        },
        {
            "content": "I'd be happy to help you create an SLA for your telemedicine platform. To get started, could you tell me more about your specific needs and any key requirements for this platform?",
            "role": "assistant",
            "timestamp": datetime.now() - timedelta(minutes=29)
        },
        {
            "content": "We need to ensure HIPAA compliance, high uptime, and quick support responses for our healthcare clients.",
            "role": "user",
            "timestamp": datetime.now() - timedelta(minutes=28)
        },
        {
            "content": "Thank you for providing that information. For a healthcare telemedicine platform, HIPAA compliance, high uptime, and responsive support are indeed critical. Let me ask some specific questions to help create your SLA:\n\n1. What uptime percentage are you looking to guarantee?\n2. What response time targets do you have for different support ticket priorities?\n3. Are there specific data security and privacy measures beyond HIPAA that you need to address?",
            "role": "assistant",
            "timestamp": datetime.now() - timedelta(minutes=27)
        }
    ]
    
    for msg_data in discovery_messages:
        from app.models.database import Message as DBMessage
        
        message = DBMessage(
            content=msg_data["content"],
            role=msg_data["role"],
            session_id=discovery_session.id,
            timestamp=msg_data["timestamp"]
        )
        db.add(message)
    
    # Create a template creation session
    template_session = DBConsultationSession(
        user_id=user_id,
        session_type="template_creation",
        context_data={
            "industry": "Technology",
            "service_type": "SaaS Application",
            "key_metrics": ["Uptime", "Response Time", "Resolution Time"]
        },
        recommendations={
            "recommended_metrics": [
                {"name": "Service Uptime", "target": 99.9, "unit": "%"},
                {"name": "Response Time", "target": 200, "unit": "ms"},
                {"name": "Time to Resolve Critical Issues", "target": 4, "unit": "hours"}
            ],
            "recommended_terms": [
                "Credits are applied to the next billing cycle",
                "Customer must report SLA violations within 5 business days"
            ]
        }
    )
    
    db.add(template_session)
    db.flush()  # Get the ID without committing
    
    # Create messages for the template creation session
    template_messages = [
        {
            "content": "I'd like to create an SLA template for our SaaS application.",
            "role": "user",
            "timestamp": datetime.now() - timedelta(hours=2)
        },
        {
            "content": "I'll help you create an SLA template for your SaaS application. Could you tell me what specific service levels you want to guarantee?",
            "role": "assistant",
            "timestamp": datetime.now() - timedelta(hours=2, minutes=58)
        },
        {
            "content": "We need to guarantee uptime, fast response times, and quick resolution of critical issues.",
            "role": "user",
            "timestamp": datetime.now() - timedelta(hours=2, minutes=55)
        },
        {
            "content": "Based on industry standards for SaaS applications, I recommend including the following metrics in your SLA:\n\n1. Service Uptime: 99.9%\n2. Response Time: 200ms\n3. Time to Resolve Critical Issues: 4 hours\n\nWould you like to adjust any of these targets?",
            "role": "assistant",
            "timestamp": datetime.now() - timedelta(hours=2, minutes=53)
        }
    ]
    
    for msg_data in template_messages:
        from app.models.database import Message as DBMessage
        
        message = DBMessage(
            content=msg_data["content"],
            role=msg_data["role"],
            session_id=template_session.id,
            timestamp=msg_data["timestamp"]
        )
        db.add(message)
    
    # Commit all changes
    db.commit()
    print(f"Created 2 consultation sessions with messages for user_id: {user_id}")

if __name__ == "__main__":
    init_consultations()