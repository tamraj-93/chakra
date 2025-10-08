"""
Models for consultation templates and stages.
These models define the structure for guided conversations and consultations.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
from datetime import datetime


class StageType(str, Enum):
    """Types of stages in a consultation template."""
    INFORMATION_GATHERING = "information_gathering"
    PROBLEM_ANALYSIS = "problem_analysis"
    RECOMMENDATION = "recommendation"
    FOLLOW_UP = "follow_up"
    SUMMARY = "summary"


class ExpectedOutput(BaseModel):
    """Expected output from a consultation stage."""
    name: str
    description: str
    data_type: str  # text, number, boolean, list, object
    required: bool = True


class ConsultationStage(BaseModel):
    """A stage in a consultation template."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    stage_type: StageType
    prompt_template: str
    system_instructions: str
    expected_outputs: List[ExpectedOutput]
    ui_components: Dict[str, Any] = {}  # Configuration for UI components to display
    next_stage_conditions: Dict[str, str] = {}  # Conditions to determine next stage
    
    @validator('prompt_template')
    def prompt_template_not_empty(cls, v):
        if not v:
            raise ValueError("prompt_template cannot be empty")
        return v


class ConsultationTemplateBase(BaseModel):
    """Base model for consultation templates."""
    name: str
    description: str
    domain: str  # e.g., healthcare, tech_support, financial_advisory
    version: str = "1.0"
    tags: List[str] = []
    initial_system_prompt: str
    stages: List[ConsultationStage]
    
    @validator('stages')
    def at_least_one_stage(cls, v):
        if not v:
            raise ValueError("template must have at least one stage")
        return v


class ConsultationTemplateCreate(ConsultationTemplateBase):
    """Model for creating a new consultation template."""
    pass


class ConsultationTemplate(ConsultationTemplateBase):
    """Complete consultation template model with database fields."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[int] = None
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class ConsultationSessionState(BaseModel):
    """State of an ongoing consultation session."""
    template_id: str
    current_stage_id: str
    completed_stages: List[str] = []
    collected_data: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


# Extended ConsultationSession model to support templates
class ConsultationSessionExtended(BaseModel):
    """Extended consultation session model with template information."""
    id: int
    user_id: int
    template_id: Optional[str] = None
    session_type: str  # 'discovery', 'template_guided', 'analysis'
    session_state: Optional[ConsultationSessionState] = None
    context_data: Dict[str, Any] = {}
    recommendations: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True