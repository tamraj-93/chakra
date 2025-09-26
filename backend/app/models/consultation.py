from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MessageBase(BaseModel):
    content: str
    role: str  # 'user', 'assistant', or 'system'

class Message(MessageBase):
    id: int
    session_id: int
    timestamp: str

    class Config:
        orm_mode = True

class ConsultationSession(BaseModel):
    id: int
    user_id: int
    session_type: str  # 'discovery', 'template_creation', 'analysis'
    context_data: Dict[str, Any]
    recommendations: Dict[str, Any]
    created_at: str

    class Config:
        orm_mode = True