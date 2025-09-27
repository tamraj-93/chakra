"""
Script to initialize the database with sample data for testing.
Run this script with:
    python -m scripts.init_db
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.models import database as db_models
from app.services import user as user_service
import json

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Check if we already have users
        user_count = db.query(db_models.User).count()
        
        if user_count == 0:
            print("Creating sample users...")
            create_sample_users(db)
            
        # Check if we already have metrics
        metric_count = db.query(db_models.SLAMetric).count()
        
        if metric_count == 0:
            print("Creating sample SLA metrics...")
            create_sample_metrics(db)
            
        # Check if we already have templates
        template_count = db.query(db_models.SLATemplate).count()
        
        if template_count == 0 and user_count > 0:
            print("Creating sample SLA templates...")
            create_sample_templates(db)
            
        print("Database initialization completed!")
        
    finally:
        db.close()

def create_sample_users(db: Session):
    # Create admin user
    from app.models.user import UserCreate
    
    admin_data = UserCreate(email="admin@example.com", password="password")
    admin = user_service.create_user(
        db=db,
        user=admin_data
    )
    
    # Create regular user
    user_data = UserCreate(email="user@example.com", password="password")
    user = user_service.create_user(
        db=db,
        user=user_data
    )
    
    print(f"Created users: admin@example.com and user@example.com (password: password)")

def create_sample_metrics(db: Session):
    # Availability metrics
    metrics = [
        db_models.SLAMetric(
            name="Service Uptime",
            category="availability",
            unit_of_measure="percentage",
            calculation_method="(uptime_minutes / total_minutes) * 100",
            industry_benchmarks={"standard": 99.9, "premium": 99.99, "enterprise": 99.999}
        ),
        db_models.SLAMetric(
            name="Error Rate",
            category="performance",
            unit_of_measure="percentage",
            calculation_method="(error_requests / total_requests) * 100",
            industry_benchmarks={"standard": 1.0, "premium": 0.5, "enterprise": 0.1}
        ),
        db_models.SLAMetric(
            name="Response Time",
            category="performance",
            unit_of_measure="milliseconds",
            calculation_method="avg(request_time)",
            industry_benchmarks={"standard": 500, "premium": 200, "enterprise": 100}
        ),
        db_models.SLAMetric(
            name="Time to Resolve Critical Issues",
            category="support",
            unit_of_measure="hours",
            calculation_method="avg(resolution_time)",
            industry_benchmarks={"standard": 8, "premium": 4, "enterprise": 2}
        ),
        db_models.SLAMetric(
            name="Security Incident Response Time",
            category="security",
            unit_of_measure="minutes",
            calculation_method="avg(incident_response_time)",
            industry_benchmarks={"standard": 60, "premium": 30, "enterprise": 15}
        )
    ]
    
    for metric in metrics:
        db.add(metric)
    
    db.commit()
    print(f"Added {len(metrics)} SLA metrics")

def create_sample_templates(db: Session):
    # Get admin user
    admin = db.query(db_models.User).filter(db_models.User.email == "admin@example.com").first()
    
    if not admin:
        print("Admin user not found, skipping template creation")
        return
    
    # Create a sample template for Cloud Services
    cloud_template = db_models.SLATemplate(
        user_id=admin.id,
        name="Cloud Hosting SLA",
        industry="Technology",
        service_type="Cloud Services",
        is_public=True,
        template_data={
            "name": "Cloud Hosting SLA",
            "description": "Service Level Agreement for cloud hosting services",
            "metrics": [
                {"name": "Service Uptime", "target": 99.9, "penalty": "10% credit if below target"},
                {"name": "Response Time", "target": 200, "penalty": "5% credit if below target"},
                {"name": "Time to Resolve Critical Issues", "target": 4, "penalty": "15% credit if below target"}
            ],
            "terms": [
                "All times are measured in the provider's local time zone",
                "Credits are applied to the next billing cycle",
                "Customer must report SLA violations within 5 business days"
            ]
        }
    )
    
    # Create a sample template for Support Services
    support_template = db_models.SLATemplate(
        user_id=admin.id,
        name="Technical Support SLA",
        industry="Customer Service",
        service_type="Support",
        is_public=True,
        template_data={
            "name": "Technical Support SLA",
            "description": "Service Level Agreement for technical support services",
            "metrics": [
                {"name": "Time to First Response", "target": 1, "unit": "hours", "penalty": "5% credit if below target"},
                {"name": "Time to Resolve Critical Issues", "target": 4, "unit": "hours", "penalty": "10% credit if below target"},
                {"name": "Customer Satisfaction", "target": 4.5, "unit": "rating (1-5)", "penalty": "5% credit if below target"}
            ],
            "terms": [
                "Support available 24/7 for critical issues",
                "Standard support hours are 9am-5pm, Monday-Friday",
                "Customer must provide all information needed to resolve issues"
            ]
        }
    )
    
    # Add templates to the database
    db.add(cloud_template)
    db.add(support_template)
    db.commit()
    print("Added sample SLA templates")

if __name__ == "__main__":
    init_db()