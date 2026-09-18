import os

files = {
    'backend/app/schemas/alert.py': '''from pydantic import BaseModel
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
''',
    'backend/app/routers/alerts.py': '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.database import models
from app.schemas import alert as schemas

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("/", response_model=List[schemas.Alert])
def get_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).order_by(models.Alert.timestamp.desc()).offset(skip).limit(limit).all()
    return alerts

@router.get("/{alert_id}", response_model=schemas.Alert)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
''',
    'backend/app/main.py': '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base
from app.routers import alerts
from app.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIH PS 013 - Threat Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0"}

@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    return {
        "status": {
            "detection_engine": "ONLINE",
            "zeek": "UNAVAILABLE",
            "ml_model": "LOADED",
            "database": "CONNECTED",
            "traffic_input": "IDLE"
        },
        "metrics": {
            "total_traffic_analyzed": 0,
            "flows_analyzed": 0,
            "threats_detected": 0,
            "critical_alerts": 0,
            "high_alerts": 0,
            "medium_alerts": 0,
            "low_alerts": 0,
            "anomalies_detected": 0
        }
    }
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
