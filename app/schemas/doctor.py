from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal

class DoctorBase(BaseModel):
    doctor_code: str
    name: str
    specialization: str
    email: EmailStr
    phone: str
    salary: Decimal
    gender: str
    address: Optional[str] = None
    status: Optional[int] = 1

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    doctor_code: Optional[str] = None
    name: Optional[str] = None
    specialization: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    salary: Optional[Decimal] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    status: Optional[int] = None

class DoctorResponse(DoctorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True