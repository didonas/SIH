import os
import shutil

files = {
    'backend/app/routers/analyze.py': '''from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import models
import shutil
import os
import time
import pandas as pd
from app.ingestion.pcap_adapter import parse_pcap_to_events
from app.feature_engineering.window_engine import create_flow_features
from app.detection.rules import evaluate_rules
from app.detection.risk_scoring import calculate_risk
from app.ml.engine import MLEngine

router = APIRouter(prefix="/api/analyze", tags=["analyze"])
ml_engine = MLEngine()

global_traffic_status = "IDLE"

@router.post("/pcap")
async def analyze_pcap(file: UploadFile = File(...), db: Session = Depends(get_db)):
    global global_traffic_status
    if not file.filename.endswith('.pcap') and not file.filename.endswith('.pcapng'):
        raise HTTPException(status_code=400, detail="Invalid file format")
        
    global_traffic_status = "ANALYZING"
    start_time = time.time()
    os.makedirs("tmp", exist_ok=True)
    safe_filename = os.path.basename(file.filename)
    file_path = f"tmp/{safe_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        events = parse_pcap_to_events(file_path)
        if not events:
            global_traffic_status = "IDLE"
            return {"message": "No events found", "alerts": []}
            
        df = create_flow_features(events)
        if df.empty:
            global_traffic_status = "IDLE"
            return {"message": "No flows detected", "alerts": []}
            
        df_rules = evaluate_rules(df)
        df = pd.concat([df, df_rules], axis=1)
        
        df_ml = ml_engine.analyze_flows(df)
        df = pd.concat([df, df_ml], axis=1)
        
        df_risk = df.apply(calculate_risk, axis=1)
        df = pd.concat([df, df_risk], axis=1)
        
        alerts_created = []
        for i, row in df.iterrows():
            if row['final_risk_score'] >= 30:
                alert = models.Alert(
                    source_ip=row['source_ip'],
                    destination_ip=row['destination_ip'],
                    source_port=int(row['source_port']),
                    destination_port=int(row['destination_port']),
                    protocol=str(row['protocol']),
                    threat_type=row['final_threat_type'],
                    severity=row['severity'],
                    risk_score=row['final_risk_score'],
                    confidence=row.get('rf_probability', 0.0),
                    model_used="Rules+ML",
                    anomaly_score=row.get('if_score', 0.0),
                    evidence=row['evidence']
                )
                db.add(alert)
                alerts_created.append(alert)
                
        db.commit()
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        history = models.DetectionHistory(
            input_source=safe_filename,
            model="Rules+ML",
            result=f"{len(alerts_created)} threats detected",
            processing_status="SUCCESS",
            events_ingested=len(events),
            flows_analyzed=len(df),
            alerts_generated=len(alerts_created),
            processing_time_ms=processing_time_ms
        )
        db.add(history)
        db.commit()
        
        global_traffic_status = "COMPLETED"
        return {
            "message": "Analysis complete",
            "events_ingested": len(events),
            "flows_analyzed": len(df),
            "threats_detected": len(alerts_created),
            "processing_time_ms": processing_time_ms
        }
    except Exception as e:
        global_traffic_status = "ERROR"
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.get("/status")
def get_traffic_status():
    global global_traffic_status
    return {"status": global_traffic_status}
''',
    'backend/app/main.py': '''from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import engine, Base, get_db
from app.database import models
from app.routers import alerts, analyze, models as models_router, system
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
'''
}

for path, content in files.items():
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
