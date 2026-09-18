from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class AlertBase(BaseModel):
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    threat_type: str
    severity: str
    risk_score: float
    confidence: float
    model_used: str
    anomaly_score: float
    evidence: Any

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    timestamp: datetime
    status: str

    class Config:
        orm_mode = True
