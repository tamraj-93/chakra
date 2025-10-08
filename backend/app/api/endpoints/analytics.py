from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

from app.core.database import get_db
from app.models import database as db_models
from app.api.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/summary")
async def get_summary_metrics(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Get summary metrics for the dashboard"""
    
    # Get total consultations
    total_consultations = db.query(db_models.ConsultationSession).count()
    
    # Get active users (users with sessions in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(db_models.User).join(
        db_models.ConsultationSession,
        db_models.User.id == db_models.ConsultationSession.user_id
    ).filter(
        db_models.ConsultationSession.created_at >= thirty_days_ago
    ).distinct().count()
    
    # Calculate average response time (mock data for now)
    avg_response_time = "1.8s"
    
    # Count templates used
    templates_used = db.query(db_models.SLATemplate).count()
    
    # Calculate trends (mock data for now)
    consultation_trend = 12.5
    users_trend = 8.3
    response_time_trend = -5.2
    
    # Return formatted metrics
    return {
        "metrics": [
            {
                "title": "Total Consultations",
                "value": str(total_consultations),
                "icon": "chat-dots",
                "trend": {"value": consultation_trend, "isPositive": True},
                "color": "linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%)"
            },
            {
                "title": "Active Users",
                "value": str(active_users),
                "icon": "people",
                "trend": {"value": users_trend, "isPositive": True},
                "color": "linear-gradient(135deg, var(--secondary) 0%, var(--secondary-light) 100%)"
            },
            {
                "title": "Avg. Response Time",
                "value": avg_response_time,
                "icon": "clock",
                "trend": {"value": abs(response_time_trend), "isPositive": response_time_trend < 0},
                "color": "linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%)"
            },
            {
                "title": "Templates Used",
                "value": str(templates_used),
                "icon": "file-earmark-text",
                "color": "linear-gradient(135deg, #26C6DA 0%, #80DEEA 100%)"
            }
        ]
    }

@router.get("/consultation-activity")
async def get_consultation_activity(
    period: str = Query("week", description="Time period: week, month, or quarter"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get consultation activity data for the specified period"""
    
    # Determine date range based on period
    today = datetime.utcnow()
    if period == "week":
        start_date = today - timedelta(days=7)
        labels = [(today - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    elif period == "month":
        start_date = today - timedelta(days=30)
        labels = [(today - timedelta(days=i)).strftime("%d %b") for i in range(29, -1, -6)]
        labels = labels[::-1]  # Reverse to get chronological order
    else:  # quarter
        start_date = today - timedelta(days=90)
        labels = [(today - timedelta(days=i*10)).strftime("%d %b") for i in range(9, -1, -1)]
    
    # For now, generate mock data
    # In a real implementation, query the database for actual consultations per day
    if period == "week":
        counts = [22, 28, 40, 32, 24, 18, 12]
    elif period == "month":
        counts = [85, 92, 120, 110, 95]
    else:  # quarter
        counts = [240, 280, 350, 400, 370, 410, 380, 350, 320, 290]
    
    # Calculate percentages
    max_count = max(counts)
    percentages = [int((count / max_count) * 100) for count in counts]
    
    # Create response data
    data = [
        {"label": label, "count": count, "percentage": percentage}
        for label, count, percentage in zip(labels, counts, percentages)
    ]
    
    return {"data": data}

@router.get("/sla-compliance")
async def get_sla_compliance(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get SLA compliance data by category"""
    
    # In a real implementation, query the database for actual compliance metrics
    # For now, return mock data
    data = [
        {"category": "Availability", "percentage": 98.2, "color": "#4CAF50"},
        {"category": "Performance", "percentage": 94.5, "color": "#2196F3"},
        {"category": "Security", "percentage": 100, "color": "#673AB7"},
        {"category": "Support", "percentage": 89.8, "color": "#FF9800"}
    ]
    
    return {"data": data}

@router.get("/sla-performance")
async def get_sla_performance(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get SLA performance metrics"""
    
    # In a real implementation, query the database for actual SLA metrics
    # For now, return mock data
    metrics = [
        {
            "name": "System Availability",
            "currentValue": 99.97,
            "threshold": 99.9,
            "unit": "%",
            "status": "success"
        },
        {
            "name": "Response Time",
            "currentValue": 1.8,
            "threshold": 2.0,
            "unit": "s",
            "status": "success"
        },
        {
            "name": "Resolution Time",
            "currentValue": 3.2,
            "threshold": 4.0,
            "unit": "hours",
            "status": "success"
        },
        {
            "name": "Security Incidents",
            "currentValue": 0,
            "threshold": 0,
            "unit": "",
            "status": "success"
        },
        {
            "name": "Support Response",
            "currentValue": 18,
            "threshold": 15,
            "unit": "min",
            "status": "warning"
        }
    ]
    
    return {"metrics": metrics}