import os

files = {
    'backend/app/routers/analyze.py': '''from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import models
import shutil
import os
from app.feature_engineering.extractor import extract_features_from_pcap
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
        # Extract features
        df = extract_features_from_pcap(file_path)
        if df.empty:
            return {"message": "No flows detected", "alerts": []}
            
        # Run ML inference
        df_results = ml_engine.analyze_flows(df)
        
        # Save alerts to DB
        alerts_created = []
        for i, row in df_results.iterrows():
            if row['threat_type'] != 'NORMAL':
                alert = models.Alert(
                    source_ip=row['source_ip'],
                    destination_ip=row['destination_ip'],
                    source_port=int(row['source_port']),
                    destination_port=int(row['destination_port']),
                    protocol=row['protocol'],
                    threat_type=row['threat_type'],
                    severity=row['severity'],
                    risk_score=row['risk_score'],
                    confidence=row['confidence'],
                    model_used="Heuristic/RF",
                    anomaly_score=row['anomaly_score'],
                    evidence=row['evidence']
                )
                db.add(alert)
                alerts_created.append(alert)
                
        db.commit()
        
        # Record history
        history = models.DetectionHistory(
            input_source=file.filename,
            model="Heuristic/RF",
            result=f"{len(alerts_created)} threats detected",
            processing_status="SUCCESS"
        )
        db.add(history)
        db.commit()
        
        return {
            "message": "Analysis complete",
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
