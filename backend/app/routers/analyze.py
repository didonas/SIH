from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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
def analyze_pcap(file: UploadFile = File(...), db: Session = Depends(get_db)):
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
                import math
                def safe_float(v):
                    try:
                        f = float(v)
                        return 0.0 if math.isnan(f) else f
                    except:
                        return 0.0

                alert = models.Alert(
                    source_ip=row['source_ip'],
                    destination_ip=row['destination_ip'],
                    source_port=int(row['source_port']),
                    destination_port=int(row['destination_port']),
                    protocol=str(row['protocol']),
                    threat_type=row['final_threat_type'],
                    severity=row['severity'],
                    risk_score=safe_float(row['final_risk_score']),
                    confidence=safe_float(row.get('rf_probability', 0.0)),
                    model_used="Rules+ML",
                    anomaly_score=safe_float(row.get('if_score', 0.0)),
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
        
        alert_list = []
        for a in alerts_created:
            alert_list.append({
                "id": a.id,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "source_ip": a.source_ip,
                "destination_ip": a.destination_ip,
                "source_port": a.source_port,
                "destination_port": a.destination_port,
                "protocol": a.protocol,
                "threat_type": a.threat_type,
                "severity": a.severity,
                "risk_score": a.risk_score,
                "confidence": a.confidence,
                "model_used": a.model_used,
                "anomaly_score": a.anomaly_score,
                "evidence": a.evidence
            })

        global_traffic_status = "COMPLETED"
        return {
            "message": "Analysis complete",
            "events_ingested": len(events),
            "flows_analyzed": len(df),
            "threats_detected": len(alerts_created),
            "processing_time_ms": processing_time_ms,
            "alerts": alert_list
        }
    except TimeoutError as te:
        global_traffic_status = "ERROR"
        raise HTTPException(status_code=408, detail=str(te))
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
