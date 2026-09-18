from fastapi import APIRouter, Depends, HTTPException
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
