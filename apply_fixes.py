import os
import shutil

files = {
    'backend/app/database/models.py': '''from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from app.database.database import Base
import datetime

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source_ip = Column(String, index=True)
    destination_ip = Column(String, index=True)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(String)
    threat_type = Column(String, index=True)
    severity = Column(String)
    risk_score = Column(Float)
    confidence = Column(Float)
    model_used = Column(String)
    anomaly_score = Column(Float)
    evidence = Column(JSON)
    status = Column(String, default='NEW')

class DetectionHistory(Base):
    __tablename__ = 'detection_history'
    id = Column(Integer, primary_key=True, index=True)
    detection_time = Column(DateTime, default=datetime.datetime.utcnow)
    input_source = Column(String)
    model = Column(String)
    result = Column(String)
    processing_status = Column(String)
    events_ingested = Column(Integer, default=0)
    flows_analyzed = Column(Integer, default=0)
    alerts_generated = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
''',
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

@router.post("/pcap")
async def analyze_pcap(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.pcap') and not file.filename.endswith('.pcapng'):
        raise HTTPException(status_code=400, detail="Invalid file format")
        
    start_time = time.time()
    os.makedirs("tmp", exist_ok=True)
    safe_filename = os.path.basename(file.filename)
    file_path = f"tmp/{safe_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        events = parse_pcap_to_events(file_path)
        if not events:
            return {"message": "No events found", "alerts": []}
            
        df = create_flow_features(events)
        if df.empty:
            return {"message": "No flows detected", "alerts": []}
            
        df_rules = evaluate_rules(df)
        df = pd.concat([df, df_rules], axis=1)
        
        df_ml = ml_engine.analyze_flows(df)
        df = pd.concat([df, df_ml], axis=1)
        
        df_risk = df.apply(calculate_risk, axis=1)
        df = pd.concat([df, df_risk], axis=1)
        
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
                    confidence=0.85,
                    model_used="Rules+ML",
                    anomaly_score=40 if row.get('if_anomaly') else 0,
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
        
        return {
            "message": "Analysis complete",
            "events_ingested": len(events),
            "flows_analyzed": len(df),
            "threats_detected": len(alerts_created),
            "processing_time_ms": processing_time_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
''',
    'backend/app/main.py': '''from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import engine, Base, get_db
from app.database import models
from app.routers import alerts, analyze, models as models_router, system
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

    return {
        "status": {
            "detection_engine": "ONLINE",
            "zeek": "UNAVAILABLE",
            "ml_model": "LOADED",
            "database": "CONNECTED",
            "traffic_input": "IDLE" if total_alerts == 0 else "ACTIVE"
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
''',
    'training_script.py': '''import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
import joblib
import os
import json

os.makedirs('training/datasets', exist_ok=True)
os.makedirs('models', exist_ok=True)

n_samples = 2000
features = ['packet_count', 'byte_count', 'duration', 'packets_per_second', 'bytes_per_second', 'syn_count', 'syn_ratio']

normal_data = pd.DataFrame({
    'packet_count': np.random.randint(1, 50, n_samples),
    'byte_count': np.random.randint(100, 10000, n_samples),
    'duration': np.random.uniform(0.1, 10.0, n_samples),
    'syn_count': np.random.randint(0, 3, n_samples),
    'label': 'NORMAL'
})
normal_data['packets_per_second'] = normal_data['packet_count'] / normal_data['duration']
normal_data['bytes_per_second'] = normal_data['byte_count'] / normal_data['duration']
normal_data['syn_ratio'] = normal_data['syn_count'] / normal_data['packet_count']

attack_data = pd.DataFrame({
    'packet_count': np.random.randint(100, 1000, n_samples),
    'byte_count': np.random.randint(5000, 100000, n_samples),
    'duration': np.random.uniform(0.01, 2.0, n_samples),
    'syn_count': np.random.randint(90, 1000, n_samples),
    'label': 'ATTACK'
})
attack_data['packets_per_second'] = attack_data['packet_count'] / attack_data['duration']
attack_data['bytes_per_second'] = attack_data['byte_count'] / attack_data['duration']
attack_data['syn_ratio'] = attack_data['syn_count'] / attack_data['packet_count']

df = pd.concat([normal_data, attack_data]).reset_index(drop=True)
df.to_csv('training/datasets/synthetic_dataset.csv', index=False)

X = df[features]
y = df['label']

# True Train/Test split for evaluation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print("--- Random Forest Evaluation (Test Set) ---")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

metrics_rf = {
    "accuracy": round(accuracy_score(y_test, y_pred), 4),
    "precision": round(precision_score(y_test, y_pred, pos_label='ATTACK'), 4),
    "recall": round(recall_score(y_test, y_pred, pos_label='ATTACK'), 4),
    "f1_score": round(f1_score(y_test, y_pred, pos_label='ATTACK'), 4)
}
print(metrics_rf)
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred, labels=['NORMAL', 'ATTACK']))

joblib.dump(rf, 'models/random_forest.pkl')
with open('models/rf_metrics.json', 'w') as f:
    json.dump(metrics_rf, f)

print("\\n--- Isolation Forest Evaluation (Test Set) ---")
# Train Isolation Forest mostly on NORMAL data to establish baseline
X_train_if = X_train[y_train == 'NORMAL']
isf = IsolationForest(contamination=0.05, random_state=42)
isf.fit(X_train_if)

# Evaluate on full test set
isf_pred = isf.predict(X_test)
# -1 is anomaly (ATTACK), 1 is normal (NORMAL)
anomaly_labels = np.where(isf_pred == -1, 'ATTACK', 'NORMAL')

metrics_if = {
    "accuracy": round(accuracy_score(y_test, anomaly_labels), 4)
}
print(metrics_if)
print("Confusion Matrix:")
print(confusion_matrix(y_test, anomaly_labels, labels=['NORMAL', 'ATTACK']))

joblib.dump(isf, 'models/isolation_forest.pkl')
with open('models/if_metrics.json', 'w') as f:
    json.dump(metrics_if, f)
'''
}

for path, content in files.items():
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

if os.path.exists('backend/sql_app.db'):
    os.remove('backend/sql_app.db')
