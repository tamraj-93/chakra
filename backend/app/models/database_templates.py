"""
Database models for consultation templates and stages.
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, DateTime, Text, Table
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


# Association table for template tags
template_tags = Table(
    "template_tags",
    Base.metadata,
    Column("template_id", String, ForeignKey("consultation_templates.id")),
    Column("tag_name", String, ForeignKey("tags.name"))
)


class ConsultationTemplate(Base):
    __tablename__ = "consultation_templates"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, index=True)
    description = Column(Text)
    domain = Column(String, index=True)
    version = Column(String)
    initial_system_prompt = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="consultation_templates")
    stages = relationship("ConsultationStage", back_populates="template", cascade="all, delete-orphan")
    tags = relationship(
        "Tag", 
        secondary=template_tags, 
        back_populates="templates",
        primaryjoin="ConsultationTemplate.id==template_tags.c.template_id",
        secondaryjoin="Tag.name==template_tags.c.tag_name"
    )
    # Using string references for the relationship to avoid circular imports
    sessions = relationship(
        "ConsultationSession", 
        primaryjoin="ConsultationTemplate.id==ConsultationSession.template_id",
        backref="template"
    )


class ConsultationStage(Base):
    __tablename__ = "consultation_stages"

    id = Column(String, primary_key=True, default=generate_uuid)
    template_id = Column(String, ForeignKey("consultation_templates.id"))
    name = Column(String)
    description = Column(Text)
    stage_type = Column(String)
    prompt_template = Column(Text)
    system_instructions = Column(Text)
    ui_components = Column(JSON)
    next_stage_conditions = Column(JSON)
    sequence_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("ConsultationTemplate", back_populates="stages")
    expected_outputs = relationship("ExpectedOutput", back_populates="stage", cascade="all, delete-orphan")


class ExpectedOutput(Base):
    __tablename__ = "expected_outputs"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(String, ForeignKey("consultation_stages.id"))
    name = Column(String)
    description = Column(Text)
    data_type = Column(String)
    required = Column(Boolean, default=True)

    # Relationships
    stage = relationship("ConsultationStage", back_populates="expected_outputs")


class Tag(Base):
    __tablename__ = "tags"

    name = Column(String, primary_key=True)
    description = Column(String, nullable=True)

    # Relationships
    templates = relationship(
        "ConsultationTemplate", 
        secondary=template_tags, 
        back_populates="tags",
        primaryjoin="Tag.name==template_tags.c.tag_name",
        secondaryjoin="ConsultationTemplate.id==template_tags.c.template_id"
    )


# Import the existing ConsultationSession and User classes to modify them
from app.models.database import ConsultationSession, User

# Add consultation_templates relationship to User
User.consultation_templates = relationship("ConsultationTemplate", back_populates="owner")