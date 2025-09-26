from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SLAMetric(BaseModel):
    id: int
    name: str
    category: str  # 'availability', 'performance', 'security', 'support'
    unit_of_measure: str
    calculation_method: str
    industry_benchmarks: Dict[str, Any]
    compliance_mappings: Dict[str, Any]

    class Config:
        orm_mode = True

class SLATemplate(BaseModel):
    id: int
    user_id: int
    name: str
    industry: str
    service_type: str
    template_data: Dict[str, Any]
    is_public: bool
    created_at: str

    class Config:
        orm_mode = True