from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any
from pydantic import field_validator

class UserBase(BaseModel):
    email: str
    name: str
    role: str
    status: str
    profile_image_url: Optional[str] = Field(None, alias="profileImageUrl")
    worker_id: str = Field(alias="workerId")

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    profile_image_url: Optional[str] = Field(None, alias="profileImageUrl")

class UserResponse(UserBase):
    id: str
    created: Any
    
    @field_validator('created')
    @classmethod
    def validate_created(cls, v):
        """Convert Firebase DatetimeWithNanoseconds to string"""
        if hasattr(v, 'isoformat'):
            return v.isoformat()
        elif hasattr(v, 'strftime'):
            return v.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return str(v)

class UserPerformance(BaseModel):
    user_id: str
    worker_id: str
    name: str
    email: str
    role: str
    performance_cluster: int
    performance_score: float
    total_work_hours: float
    attendance_rate: float
    productivity_metrics: dict