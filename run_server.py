"""
Script untuk menjalankan server dengan konfigurasi yang tepat
"""

import uvicorn
import os
import sys
from app.core.config import settings

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import firebase_admin
        import sklearn
        import pandas
        import numpy
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_firebase_setup():
    """Check if Firebase is properly configured"""
    if not os.path.exists("config/firebase-credentials.json"):
        print("❌ Firebase credentials not found!")
        print("Please add your Firebase service account key to config/firebase-credentials.json")
        return False
    
    if not settings.FIREBASE_PROJECT_ID or settings.FIREBASE_PROJECT_ID == "your-firebase-project-id":
        print("❌ Firebase project ID not configured!")
        print("Please update FIREBASE_PROJECT_ID in .env file")
        return False
    
    print("✅ Firebase configuration looks good")
    return True

def main():
    print("🚀 Employee Performance Analytics API")
    print("=" * 50)
    
    # Create necessary directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # Check requirements
    if not check_requirements():
        print("⚠️ Some packages are missing, but server will start anyway.")
    
    # Check Firebase setup
    if not check_firebase_setup():
        print("\n⚠️ Firebase not properly configured, but server will start anyway.")
        print("Some features may not work until Firebase is configured.")
    
    print(f"\n📊 Server Configuration:")
    print(f"   • Host: {settings.API_HOST}")
    print(f"   • Port: {settings.API_PORT}")
    print(f"   • Debug: {settings.DEBUG}")
    print(f"   • ML Model Path: {settings.ML_MODEL_PATH}")
    print(f"   • Clustering Clusters: {settings.CLUSTERING_N_CLUSTERS}")
    
    print(f"\n🌐 API Endpoints:")
    print(f"   • API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"   • Health Check: http://{settings.API_HOST}:{settings.API_PORT}/health")
    print(f"   • Attendance API: http://{settings.API_HOST}:{settings.API_PORT}/api/v1/attendance")
    print(f"   • Users API: http://{settings.API_HOST}:{settings.API_PORT}/api/v1/users")
    print(f"   • Analytics API: http://{settings.API_HOST}:{settings.API_PORT}/api/v1/analytics")
    print(f"   • ML API: http://{settings.API_HOST}:{settings.API_PORT}/api/v1/ml")
    
    print(f"\n🔥 Starting server...")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.DEBUG,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("Make sure all dependencies are installed and Firebase is configured properly.")

if __name__ == "__main__":
    main()
