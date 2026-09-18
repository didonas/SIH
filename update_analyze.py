import os

files = {
    'backend/app/routers/analyze.py': '''from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import models
import shutil
import os
import pandas as pd
from app.ingestion.pcap_adapter import parse_pcap_to_events
from app.feature_engineering.window_engine import create_flow_features
from app.detection.rules import evaluate_rules
from app.detection.risk_scoring import calculate_risk
from app.ml.engine import MLEngine

router = APIRouter(prefix="/api/analyze", tags=["analyze"])
ml_engine = MLEngine()

@router.post("/pcap")
async def analyze_pcap(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.pcap') and not file.filename.endswith('.pcapng'):
        raise HTTPException(status_code=400, detail="Invalid file format")
        
    os.makedirs("tmp", exist_ok=True)
    file_path = f"tmp/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Ingestion
        events = parse_pcap_to_events(file_path)
        if not events:
            return {"message": "No events found", "alerts": []}
            
        # Feature extraction
        df = create_flow_features(events)
        if df.empty:
            return {"message": "No flows detected", "alerts": []}
            
        # Rules and Statistics
        df_rules = evaluate_rules(df)
        df = pd.concat([df, df_rules], axis=1)
        
        # ML Inference
        df_ml = ml_engine.analyze_flows(df)
        df = pd.concat([df, df_ml], axis=1)
        
        # Risk Scoring
        df_risk = df.apply(calculate_risk, axis=1)
        df = pd.concat([df, df_risk], axis=1)
        
        # Save alerts to DB
        alerts_created = []
        for i, row in df.iterrows():
            if row['final_threat_type'] != 'NORMAL' or row['final_risk_score'] > 0:
                alert = models.Alert(
                    source_ip=row['source_ip'],
                    destination_ip=row['destination_ip'],
                    source_port=int(row['source_port']),
                    destination_port=int(row['destination_port']),
                    protocol=str(row['protocol']),
                    threat_type=row['final_threat_type'],
                    severity=row['severity'],
                    risk_score=row['final_risk_score'],
                    confidence=0.85, # configurable or from model proba
                    model_used="Rules+ML",
                    anomaly_score=40 if row.get('if_anomaly') else 0,
                    evidence=row['evidence']
                )
                db.add(alert)
                alerts_created.append(alert)
                
        db.commit()
        
        # Record history
        history = models.DetectionHistory(
            input_source=file.filename,
            model="Rules+ML",
            result=f"{len(alerts_created)} threats detected",
            processing_status="SUCCESS"
        )
        db.add(history)
        db.commit()
        
        return {
            "message": "Analysis complete",
            "events_ingested": len(events),
            "flows_analyzed": len(df),
            "threats_detected": len(alerts_created)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
