from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from app.services.firebase_service import firebase_service
from app.services.ml_service import ml_service

router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Get overall analytics overview"""
    try:
        # Get all active workers
        workers = await firebase_service.get_users_by_role("worker")
        
        if not workers:
            return {
                "total_workers": 0,
                "total_attendance_records": 0,
                "average_daily_hours": 0,
                "total_work_hours": 0
            }
        
        # Get attendance data
        filters = []
        if date_from:
            filters.append(("date", ">=", date_from))
        if date_to:
            filters.append(("date", "<=", date_to))
        
        attendance_records = await firebase_service.query_collection(
            "attendance",
            filters=filters
        )
        
        # Calculate metrics
        total_work_minutes = sum(record.get('workMinutes', 0) for record in attendance_records)
        total_work_hours = total_work_minutes / 60
        
        average_daily_hours = total_work_hours / len(attendance_records) if attendance_records else 0
        
        # Count unique users with attendance
        unique_users = len(set(record.get('userId') for record in attendance_records))
        
        return {
            "total_workers": len(workers),
            "active_workers": unique_users,
            "total_attendance_records": len(attendance_records),
            "average_daily_hours": round(average_daily_hours, 2),
            "total_work_hours": round(total_work_hours, 2),
            "date_range": {
                "from": date_from,
                "to": date_to
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics overview: {str(e)}")

@router.get("/team/performance")
async def get_team_performance_analytics(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    role: Optional[str] = Query("worker")
):
    """Get performance analytics for all team members"""
    try:
        # Get users
        users = await firebase_service.get_users_by_role(role)
        
        if not users:
            return []
        
        team_performance = []
        
        for user in users:
            try:
                # Calculate metrics for each user
                metrics = await ml_service.calculate_performance_metrics(
                    user['id'], date_from, date_to
                )
                
                user_performance = {
                    "user_id": user['id'],
                    "name": user.get('name'),
                    "worker_id": user.get('workerId'),
                    "email": user.get('email'),
                    "performance_metrics": metrics.dict()
                }
                
                team_performance.append(user_performance)
                
            except Exception as user_error:
                print(f"Error calculating metrics for user {user['id']}: {user_error}")
                continue
        
        # Sort by overall performance score
        team_performance.sort(
            key=lambda x: x['performance_metrics']['productivity_score'], 
            reverse=True
        )
        
        return team_performance
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting team performance: {str(e)}")

@router.get("/productivity/ranking")
async def get_productivity_ranking(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: Optional[int] = Query(10)
):
    """Get productivity ranking of workers"""
    try:
        # Get team performance
        team_performance = await get_team_performance_analytics(date_from, date_to)
        
        # Sort by productivity score and limit results
        ranking = sorted(
            team_performance,
            key=lambda x: x['performance_metrics']['productivity_score'],
            reverse=True
        )[:limit]
        
        # Add ranking position
        for i, worker in enumerate(ranking):
            worker['rank'] = i + 1
        
        return ranking
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting productivity ranking: {str(e)}")

@router.get("/trends/daily")
async def get_daily_trends(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Get daily trends analytics"""
    try:
        filters = []
        if date_from:
            filters.append(("date", ">=", date_from))
        if date_to:
            filters.append(("date", "<=", date_to))
        
        attendance_records = await firebase_service.query_collection(
            "attendance",
            filters=filters,
            order_by="date"
        )
        
        # Group by date
        daily_data = {}
        for record in attendance_records:
            date = record.get('date')
            if date not in daily_data:
                daily_data[date] = {
                    'total_hours': 0,
                    'total_overtime': 0,
                    'worker_ids': set()
                }
            
            daily_data[date]['total_hours'] += record.get('workMinutes', 0) / 60
            daily_data[date]['total_overtime'] += record.get('overtimeMinutes', 0) / 60
            daily_data[date]['worker_ids'].add(record.get('userId'))
        
        # Convert to list format
        trends = []
        for date, data in sorted(daily_data.items()):
            trends.append({
                'date': date,
                'total_hours': round(data['total_hours'], 2),
                'total_overtime': round(data['total_overtime'], 2),
                'unique_workers': len(data['worker_ids']),
                'average_hours_per_worker': round(
                    data['total_hours'] / len(data['worker_ids']) if data['worker_ids'] else 0, 2
                )
            })
        
        return {
            "daily_trends": trends,
            "summary": {
                "total_days": len(trends),
                "average_daily_workers": round(
                    sum(day['unique_workers'] for day in trends) / len(trends) if trends else 0, 2
                ),
                "average_daily_hours": round(
                    sum(day['total_hours'] for day in trends) / len(trends) if trends else 0, 2
                )
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting daily trends: {str(e)}")