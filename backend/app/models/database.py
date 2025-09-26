from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    subscription_type = Column(String, default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    templates = relationship("SLATemplate", back_populates="owner")
    sessions = relationship("ConsultationSession", back_populates="owner")


class SLATemplate(Base):
    __tablename__ = "sla_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    industry = Column(String, index=True)
    service_type = Column(String, index=True)
    template_data = Column(JSON)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="templates")


class SLAMetric(Base):
    __tablename__ = "sla_metrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)  # availability, performance, security, support
    unit_of_measure = Column(String)
    calculation_method = Column(String)
    industry_benchmarks = Column(JSON)
    compliance_mappings = Column(JSON)


class ConsultationSession(Base):
    __tablename__ = "consultation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_type = Column(String, index=True)  # discovery, template_creation, analysis
    context_data = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("consultation_sessions.id"))
    content = Column(String)
    role = Column(String)  # user, assistant, or system
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ConsultationSession", back_populates="messages")


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tokens_consumed = Column(Integer)
    endpoint = Column(String)
    session_id = Column(Integer, ForeignKey("consultation_sessions.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)