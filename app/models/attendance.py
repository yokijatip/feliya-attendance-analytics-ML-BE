from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any
from pydantic import field_validator

class AttendanceBase(BaseModel):
    attendance_id: str = Field(alias="attendanceId")
    user_id: str = Field(alias="userId")
    project_id: str = Field(alias="projectId")
    date: str
    clock_in_time: str = Field(alias="clockInTime")
    clock_out_time: Optional[str] = Field(None, alias="clockOutTime")
    total_hours_formatted: str = Field(alias="totalHoursFormatted")
    total_minutes: int = Field(alias="totalMinutes")
    work_hours_formatted: str = Field(alias="workHoursFormatted")
    work_minutes: int = Field(alias="workMinutes")
    overtime_hours_formatted: str = Field(alias="overtimeHoursFormatted")
    overtime_minutes: int = Field(alias="overtimeMinutes")
    work_description: str = Field(alias="workDescription")
    work_proof_in: str = Field(alias="workProofIn")
    work_proof_out: Optional[str] = Field(None, alias="workProofOut")
    status: str

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    clock_out_time: Optional[str] = Field(None, alias="clockOutTime")
    total_hours_formatted: Optional[str] = Field(None, alias="totalHoursFormatted")
    total_minutes: Optional[int] = Field(None, alias="totalMinutes")
    work_hours_formatted: Optional[str] = Field(None, alias="workHoursFormatted")
    work_minutes: Optional[int] = Field(None, alias="workMinutes")
    overtime_hours_formatted: Optional[str] = Field(None, alias="overtimeHoursFormatted")
    overtime_minutes: Optional[int] = Field(None, alias="overtimeMinutes")
    work_proof_out: Optional[str] = Field(None, alias="workProofOut")
    status: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: str
    
    @field_validator('clock_in_time', 'clock_out_time', mode='before')
    @classmethod
    def validate_time_fields(cls, v):
        """Handle Firebase datetime fields"""
        if hasattr(v, 'isoformat'):
            return v.isoformat()
        elif hasattr(v, 'strftime'):
            return v.strftime('%H:%M')
        return str(v) if v else None

class AttendanceAnalytics(BaseModel):
    user_id: str
    total_work_hours: float
    total_overtime_hours: float
    attendance_rate: float
    average_daily_hours: float
    punctuality_score: float
    productivity_score: float