from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from app.core.config import settings
from app.api.routes import attendance, users, analytics, ml_clustering
from app.services.firebase_service import firebase_service
from app.services.ml_service import ml_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n🚀 EMPLOYEE PERFORMANCE ANALYTICS API")
    print("="*50)
    print("🔥 Initializing services...")
    
    firebase_service.initialize()
    await ml_service.initialize()
    
    # Run different types of analysis
    print("\n" + "="*60)
    print("📊 RUNNING MULTIPLE ANALYSIS PERIODS")
    print("="*60)
    
    # 1. All-time analysis (default)
    await ml_service.run_startup_analysis()
    
    # 2. Current month analysis
    await ml_service.run_monthly_analysis()
    
    # 3. Current quarter analysis  
    await ml_service.run_quarterly_analysis()
    
    print("\n✅ All services initialized successfully!")
    print("🌐 API is ready to serve requests")
    print("📊 All clustering analyses completed")
    print("="*50)
    
    yield
    
    # Shutdown
    print("\n🔄 Shutting down services...")
    print("👋 Goodbye!")

app = FastAPI(
    title="Employee Performance Analytics API",
    description="Backend API untuk analisis performa karyawan dengan K-Means clustering dan Firebase integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["attendance"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(ml_clustering.router, prefix="/api/v1/ml", tags=["machine-learning"])

@app.get("/")
async def root():
    return {
        "message": "Employee Performance Analytics API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "features": [
            "Firebase Firestore Integration",
            "K-Means Clustering Analysis",
            "Performance Metrics Calculation",
            "Real-time Analytics",
            "AI-powered Insights"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "firebase_connected": firebase_service.db is not None,
        "ml_model_trained": ml_service.kmeans_model is not None
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )