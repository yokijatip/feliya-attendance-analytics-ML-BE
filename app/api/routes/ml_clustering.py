from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict
import asyncio
import logging

from app.models.ml_models import ClusteringRequest, ClusteringResponse, PerformanceInsights
from app.services.ml_service import ml_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/clustering/analyze", response_model=ClusteringResponse)
async def perform_clustering_analysis(
    request: ClusteringRequest,
    background_tasks: BackgroundTasks
):
    """Perform K-Means clustering analysis on employee performance data"""
    try:
        # Add background task for model saving
        result = await ml_service.perform_clustering(
            user_ids=request.user_ids,
            date_from=request.date_from,
            date_to=request.date_to,
            n_clusters=request.n_clusters
        )
        
        # Save visualization in background
        background_tasks.add_task(ml_service.create_visualizations_async, result)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Clustering analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Error performing clustering analysis: {str(e)}")

@router.get("/clustering/quick-analysis", response_model=ClusteringResponse)
async def quick_clustering_analysis(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    n_clusters: Optional[int] = Query(3),
    background_tasks: BackgroundTasks = None
):
    """Perform quick clustering analysis on all active workers with enhanced error handling"""
    try:
        result = await ml_service.perform_clustering(
            user_ids=None,  # All workers
            date_from=date_from,
            date_to=date_to,
            n_clusters=n_clusters
        )
        
        # Create visualization in background if requested
        if background_tasks:
            background_tasks.add_task(ml_service.create_visualizations_async, result)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Quick analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Error performing quick analysis: {str(e)}")

@router.get("/clustering/model-status")
async def get_model_status():
    """Get detailed information about the current clustering model"""
    try:
        return {
            "model_trained": ml_service.kmeans_model is not None,
            "available_clusters": len(ml_service.cluster_labels),
            "cluster_labels": ml_service.cluster_labels,
            "feature_names": ml_service.feature_names,
            "model_metadata": ml_service.model_metadata,
            "model_info": {
                "algorithm": "K-Means",
                "n_clusters": len(ml_service.cluster_labels),
                "features_count": len(ml_service.feature_names),
                "last_trained": ml_service.model_metadata.get('last_trained'),
                "training_data_size": ml_service.model_metadata.get('training_data_size', 0)
            }
        }
    
    except Exception as e:
        logger.error(f"Model status error: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting model status: {str(e)}")

@router.post("/clustering/retrain")
async def retrain_model(
    background_tasks: BackgroundTasks,
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    n_clusters: Optional[int] = Query(3)
):
    """Retrain the clustering model with new data"""
    try:
        logger.info("🔄 Starting model retraining...")
        
        # Perform clustering which will retrain the model
        result = await ml_service.perform_clustering(
            user_ids=None,
            date_from=date_from,
            date_to=date_to,
            n_clusters=n_clusters
        )
        
        # Create new visualizations in background
        background_tasks.add_task(ml_service.create_visualizations_async, result)
        
        return {
            "message": "Model retrained successfully",
            "model_accuracy": result.model_accuracy,
            "total_users": result.total_users,
            "retrained_at": ml_service.model_metadata.get('last_trained')
        }
    
    except Exception as e:
        logger.error(f"Model retraining error: {e}")
        raise HTTPException(status_code=500, detail=f"Error retraining model: {str(e)}")

@router.get("/clustering/export-results")
async def export_clustering_results(
    format: str = Query("json", regex="^(json|csv)$"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Export clustering results in different formats"""
    try:
        result = await ml_service.perform_clustering(
            date_from=date_from,
            date_to=date_to
        )
        
        if format == "csv":
            import pandas as pd
            from io import StringIO
            from fastapi.responses import StreamingResponse
            
            # Convert to DataFrame
            data = []
            for r in result.results:
                row = {
                    'user_id': r.user_id,
                    'worker_id': r.worker_id,
                    'name': r.name,
                    'cluster': r.cluster,
                    'cluster_label': r.cluster_label,
                    'performance_score': r.performance_score,
                    **r.features
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            return StreamingResponse(
                iter([csv_buffer.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=clustering_results.csv"}
            )
        
        return result  # JSON format
    
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting results: {str(e)}")
