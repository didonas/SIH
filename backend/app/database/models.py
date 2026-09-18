from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
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
