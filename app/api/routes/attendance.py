from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.models.attendance import AttendanceResponse, AttendanceCreate, AttendanceUpdate
from app.services.firebase_service import firebase_service

router = APIRouter()

@router.get("/", response_model=List[AttendanceResponse])
async def get_all_attendance(
    user_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: Optional[int] = Query(100)
):
    """Get attendance records with optional filtering"""
    try:
        filters = []
        
        if user_id:
            filters.append(("userId", "==", user_id))
        if date_from:
            filters.append(("date", ">=", date_from))
        if date_to:
            filters.append(("date", "<=", date_to))
        
        attendance_records = await firebase_service.query_collection(
            "attendance", 
            filters=filters,
            order_by="date",
            limit=limit
        )
        
        return [AttendanceResponse(**record) for record in attendance_records]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")

@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(attendance_id: str):
    """Get specific attendance record"""
    try:
        attendance = await firebase_service.get_document("attendance", attendance_id)
        if not attendance:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        return AttendanceResponse(**attendance)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")

@router.get("/user/{user_id}/summary")
async def get_user_attendance_summary(
    user_id: str,
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Get attendance summary for a specific user"""
    try:
        attendance_records = await firebase_service.get_attendance_by_user(
            user_id, date_from, date_to
        )
        
        if not attendance_records:
            return {
                "user_id": user_id,
                "total_records": 0,
                "total_work_hours": 0,
                "total_overtime_hours": 0,
                "average_daily_hours": 0
            }
        
        total_work_minutes = sum(record.get('workMinutes', 0) for record in attendance_records)
        total_overtime_minutes = sum(record.get('overtimeMinutes', 0) for record in attendance_records)
        
        total_work_hours = total_work_minutes / 60
        total_overtime_hours = total_overtime_minutes / 60
        average_daily_hours = total_work_hours / len(attendance_records) if attendance_records else 0
        
        return {
            "user_id": user_id,
            "total_records": len(attendance_records),
            "total_work_hours": round(total_work_hours, 2),
            "total_overtime_hours": round(total_overtime_hours, 2),
            "average_daily_hours": round(average_daily_hours, 2),
            "date_range": {
                "from": date_from,
                "to": date_to
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting attendance summary: {str(e)}")