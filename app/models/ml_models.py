from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ClusteringRequest(BaseModel):
    user_ids: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    n_clusters: Optional[int] = 3

class ClusteringResult(BaseModel):
    user_id: str
    worker_id: str
    name: str
    cluster: int
    cluster_label: str
    performance_score: float
    features: Dict[str, float]

class ClusteringResponse(BaseModel):
    results: List[ClusteringResult]
    cluster_centers: Dict[str, List[float]]
    feature_names: List[str]
    analysis_period: Dict[str, str]
    total_users: int
    model_accuracy: float

class PerformanceMetrics(BaseModel):
    user_id: str
    total_work_hours: float
    average_daily_hours: float
    attendance_rate: float
    overtime_ratio: float
    punctuality_score: float
    consistency_score: float
    productivity_score: float

class PerformanceInsights(BaseModel):
    user_id: str
    insights: List[str]
    recommendations: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]