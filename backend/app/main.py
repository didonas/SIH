from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import engine, Base, get_db
from app.database import models
from app.routers import alerts, analyze, models as models_router, system, live
from app.config import settings
import shutil
import os

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
app.include_router(analyze.router)
app.include_router(models_router.router)
app.include_router(system.router)
app.include_router(live.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0"}

@app.get("/api/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_alerts = db.query(models.Alert).count()
    critical = db.query(models.Alert).filter(models.Alert.severity == 'CRITICAL').count()
    high = db.query(models.Alert).filter(models.Alert.severity == 'HIGH').count()
    medium = db.query(models.Alert).filter(models.Alert.severity == 'MEDIUM').count()
    low = db.query(models.Alert).filter(models.Alert.severity == 'LOW').count()
    
    flows_analyzed = db.query(func.sum(models.DetectionHistory.flows_analyzed)).scalar() or 0
    events_ingested = db.query(func.sum(models.DetectionHistory.events_ingested)).scalar() or 0
    anomalies = db.query(models.Alert).filter(models.Alert.threat_type == 'ANOMALY').count()

    zeek_status = "AVAILABLE" if shutil.which("zeek") else "UNAVAILABLE"
    rf_exists = os.path.exists('models/random_forest.pkl') or os.path.exists('../models/random_forest.pkl')
    ml_status = "LOADED" if rf_exists else "NOT LOADED"

    return {
        "status": {
            "detection_engine": "ONLINE",
            "zeek": zeek_status,
            "ml_model": ml_status,
            "database": "CONNECTED",
            "traffic_input": analyze.global_traffic_status
        },
        "metrics": {
            "total_traffic_analyzed": events_ingested,
            "flows_analyzed": flows_analyzed,
            "threats_detected": total_alerts,
            "critical_alerts": critical,
            "high_alerts": high,
            "medium_alerts": medium,
            "low_alerts": low,
            "anomalies_detected": anomalies
        }
    }

@app.get("/api/dashboard/analytics")
def get_traffic_analytics(db: Session = Depends(get_db)):
    flows_analyzed = db.query(func.sum(models.DetectionHistory.flows_analyzed)).scalar() or 0
    events_ingested = db.query(func.sum(models.DetectionHistory.events_ingested)).scalar() or 0
    processing_time = db.query(func.sum(models.DetectionHistory.processing_time_ms)).scalar() or 0
    
    total_alerts = db.query(models.Alert).count()
    anomalies = db.query(models.Alert).filter(models.Alert.threat_type == 'ANOMALY').count()
    
    protocol_counts = dict(db.query(models.Alert.protocol, func.count(models.Alert.id)).group_by(models.Alert.protocol).all())
    threat_counts = dict(db.query(models.Alert.threat_type, func.count(models.Alert.id)).group_by(models.Alert.threat_type).all())
    severity_counts = dict(db.query(models.Alert.severity, func.count(models.Alert.id)).group_by(models.Alert.severity).all())
    
    top_sources = [{"ip": ip, "count": count} for ip, count in db.query(models.Alert.source_ip, func.count(models.Alert.id)).group_by(models.Alert.source_ip).order_by(func.count(models.Alert.id).desc()).limit(5).all()]
    top_destinations = [{"ip": ip, "count": count} for ip, count in db.query(models.Alert.destination_ip, func.count(models.Alert.id)).group_by(models.Alert.destination_ip).order_by(func.count(models.Alert.id).desc()).limit(5).all()]
    
    history = db.query(models.DetectionHistory).order_by(models.DetectionHistory.detection_time.asc()).all()
    timeline = [{
        "time": h.detection_time.isoformat(), 
        "events": h.events_ingested, 
        "flows": h.flows_analyzed, 
        "alerts": h.alerts_generated
    } for h in history]

    return {
        "metrics": {
            "total_events": events_ingested,
            "total_flows": flows_analyzed,
            "total_alerts": total_alerts,
            "anomalies_detected": anomalies,
            "processing_time_ms": processing_time,
            "flows_per_second": round((flows_analyzed / (processing_time / 1000))) if processing_time > 0 else 0
        },
        "distributions": {
            "protocols": protocol_counts,
            "threat_types": threat_counts,
            "severities": severity_counts,
            "top_sources": top_sources,
            "top_destinations": top_destinations
        },
        "timeline": timeline
    }
