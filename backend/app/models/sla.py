from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class SLAMetric(BaseModel):
    id: int
    name: str
    category: str  # 'availability', 'performance', 'security', 'support'
    unit_of_measure: str
    calculation_method: str
    industry_benchmarks: Dict[str, Any]
    compliance_mappings: Dict[str, Any]

    class Config:
        from_attributes = True  # Updated name for 'orm_mode' in Pydantic v2

class SLATemplate(BaseModel):
    id: int
    user_id: int
    name: str
    industry: str
    service_type: str
    template_data: Dict[str, Any]
    is_public: bool
    created_at: Any  # Accept any type (datetime or str) to avoid validation errors

    class Config:
        from_attributes = True  # Updated name for 'orm_mode' in Pydantic v2
        json_encoders = {
            # Custom encoder for datetime objects
            datetime: lambda dt: dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)
        }