import os

files = {
    'backend/app/config.py': '''import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./sql_app.db')
    MODEL_PATH: str = os.getenv('MODEL_PATH', '../models')
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    class Config:
        env_file = '.env'

settings = Settings()
''',
    'backend/app/database/database.py': '''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={'check_same_thread': False} if 'sqlite' in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
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
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
