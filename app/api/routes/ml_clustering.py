from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict

from app.models.ml_models import ClusteringRequest, ClusteringResponse, PerformanceInsights
from app.services.ml_service import ml_service

router = APIRouter()

@router.post("/clustering/analyze", response_model=ClusteringResponse)
async def perform_clustering_analysis(request: ClusteringRequest):
    """Perform K-Means clustering analysis on employee performance data"""
    try:
        result = await ml_service.perform_clustering(
            user_ids=request.user_ids,
            date_from=request.date_from,
            date_to=request.date_to,
            n_clusters=request.n_clusters
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing clustering analysis: {str(e)}")

@router.get("/clustering/quick-analysis", response_model=ClusteringResponse)
async def quick_clustering_analysis(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    n_clusters: Optional[int] = Query(3)
):
    """Perform quick clustering analysis on all active workers"""
    try:
        result = await ml_service.perform_clustering(
            user_ids=None,  # All workers
            date_from=date_from,
            date_to=date_to,
            n_clusters=n_clusters
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing quick analysis: {str(e)}")

@router.get("/clustering/user/{user_id}/predict")
async def predict_user_cluster(user_id: str):
    """Predict cluster for a specific user using trained model"""
    try:
        result = await ml_service.predict_user_cluster(user_id)
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting user cluster: {str(e)}")

@router.get("/performance/{user_id}/metrics")
async def get_user_performance_metrics(
    user_id: str,
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Get detailed performance metrics for a specific user"""
    try:
        metrics = await ml_service.calculate_performance_metrics(
            user_id, date_from, date_to
        )
        
        return {
            "user_id": user_id,
            "metrics": metrics.dict(),
            "analysis_period": {
                "date_from": date_from,
                "date_to": date_to
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating performance metrics: {str(e)}")

@router.get("/performance/{user_id}/insights", response_model=PerformanceInsights)
async def get_user_performance_insights(user_id: str):
    """Get AI-powered performance insights and recommendations"""
    try:
        insights = await ml_service.generate_performance_insights(user_id)
        return insights
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@router.post("/clustering/batch-predict")
async def batch_predict_clusters(user_ids: List[str]):
    """Predict clusters for multiple users"""
    try:
        if not ml_service.kmeans_model:
            raise HTTPException(
                status_code=400,
                detail="No trained model available. Run clustering analysis first."
            )
        
        results = []
        for user_id in user_ids:
            try:
                result = await ml_service.predict_user_cluster(user_id)
                results.append(result)
            except Exception as user_error:
                results.append({
                    "user_id": user_id,
                    "error": str(user_error)
                })
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch prediction: {str(e)}")

@router.get("/clustering/model-info")
async def get_clustering_model_info():
    """Get information about the current clustering model"""
    try:
        return {
            "available_clusters": len(ml_service.cluster_labels),
            "cluster_labels": ml_service.cluster_labels,
            "feature_names": ml_service.feature_names,
            "model_trained": ml_service.kmeans_model is not None,
            "model_info": {
                "algorithm": "K-Means",
                "n_clusters": len(ml_service.cluster_labels),
                "features_count": len(ml_service.feature_names)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")