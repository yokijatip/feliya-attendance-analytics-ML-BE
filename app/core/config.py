from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = "config/firebase-credentials.json"
    FIREBASE_PROJECT_ID: str = ""
    
    # API Configuration
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "*"
    
    # ML Configuration
    ML_MODEL_PATH: str = "models"
    CLUSTERING_N_CLUSTERS: int = 3
    
    # Performance Analysis Settings
    WORKING_HOURS_TARGET: int = 8
    PUNCTUALITY_TIME_THRESHOLD: str = "09:00"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert ALLOWED_ORIGINS string to list"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()