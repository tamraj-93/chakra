from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MessageBase(BaseModel):
    content: str
    role: str  # 'user', 'assistant', or 'system'
    stage_id: Optional[str] = None

class Message(MessageBase):
    id: int
    session_id: int
    timestamp: str

    class Config:
        from_attributes = True

class ConsultationSession(BaseModel):
    id: int
    user_id: int
    session_type: str  # 'discovery', 'template_guided', 'analysis'
    context_data: Dict[str, Any]
    recommendations: Dict[str, Any]
    created_at: str
    template_id: Optional[str] = None
    session_state: Optional[Dict[str, Any]] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True