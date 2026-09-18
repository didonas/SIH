import os

class Settings:
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./sql_app.db')
    MODEL_PATH: str = os.getenv('MODEL_PATH', '../models')
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()
