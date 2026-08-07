from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time

class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    staff_id: Optional[int] = None
    appointment_date: date
    appointment_time: time
    reason: str
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    status: str = "scheduled"
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    staff_id: Optional[int] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    reason: Optional[str] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    appointment_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AppointmentListResponse(BaseModel):
    id: int
    appointment_code: str
    patient_name: str
    doctor_name: str
    appointment_date: date
    appointment_time: time
    status: str
    reason: str
    created_at: datetime