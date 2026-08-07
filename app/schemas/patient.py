from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class PatientBase(BaseModel):
    patient_code: str
    doctor_id: int
    name: str
    age: int
    gender: str
    disease: str
    phone: str
    address: Optional[str] = None
    admission_date: date
    discharge_date: Optional[date] = None
    status: Optional[int] = 1

    @field_validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    patient_code: Optional[str] = None
    doctor_id: Optional[int] = None
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    disease: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None
    status: Optional[int] = None

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True