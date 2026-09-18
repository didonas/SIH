from fastapi import APIRouter
from app.ml.engine import MLEngine
import json
import os

router = APIRouter(prefix="/api/models", tags=["models"])

@router.get("/")
def get_models_info():
    ml_engine = MLEngine()
    
    rf_metrics = None
    if os.path.exists('../models/rf_metrics.json'):
        with open('../models/rf_metrics.json', 'r') as f:
            rf_metrics = json.load(f)
            
    if_metrics = None
    if os.path.exists('../models/if_metrics.json'):
        with open('../models/if_metrics.json', 'r') as f:
            if_metrics = json.load(f)
    
    return [
        {
            "name": "Random Forest",
            "algorithm": "Supervised Classification",
            "status": "LOADED" if ml_engine.rf_model else "NOT LOADED",
            "version": "1.0",
            "features": len(ml_engine.features),
            "metrics": rf_metrics
        },
        {
            "name": "Isolation Forest",
            "algorithm": "Unsupervised Anomaly Detection",
            "status": "LOADED" if ml_engine.if_model else "NOT LOADED",
            "version": "1.0",
            "features": len(ml_engine.features),
            "metrics": if_metrics
        }
    ]
