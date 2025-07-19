from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = "config/firebase-credentials.json"
    FIREBASE_PROJECT_ID: str = "feliya-attendance"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # ML Configuration
    ML_MODEL_PATH: str = "models"
    CLUSTERING_N_CLUSTERS: int = 3
    
    # Performance Analysis Settings
    WORKING_HOURS_TARGET: int = 8
    PUNCTUALITY_TIME_THRESHOLD: str = "09:00"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()