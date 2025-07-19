from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.models.users import UserResponse, UserCreate, UserUpdate
from app.services.firebase_service import firebase_service

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: Optional[int] = Query(100)
):
    """Get all users with optional filtering"""
    try:
        filters = []
        
        if role:
            filters.append(("role", "==", role))
        if status:
            filters.append(("status", "==", status))
        
        users = await firebase_service.query_collection(
            "users",
            filters=filters,
            limit=limit
        )
        
        return [UserResponse(**user) for user in users]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get specific user"""
    try:
        user = await firebase_service.get_document("users", user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(**user)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.get("/workers/active", response_model=List[UserResponse])
async def get_active_workers():
    """Get all active workers"""
    try:
        users = await firebase_service.query_collection(
            "users",
            filters=[
                ("role", "==", "worker"),
                ("status", "==", "active")
            ]
        )
        
        return [UserResponse(**user) for user in users]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching active workers: {str(e)}")

@router.get("/worker/{worker_id}", response_model=UserResponse)
async def get_user_by_worker_id(worker_id: str):
    """Get user by worker ID"""
    try:
        users = await firebase_service.query_collection(
            "users",
            filters=[("workerId", "==", worker_id)],
            limit=1
        )
        
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(**users[0])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")