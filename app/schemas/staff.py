from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class StaffBase(BaseModel):
    staff_code: str
    doctor_id: Optional[int] = None
    name: str
    email: EmailStr
    phone: str
    department: str
    designation: str
    salary: Decimal
    joining_date: date
    address: Optional[str] = None
    status: Optional[int] = 1

    @field_validator('salary')
    def validate_salary(cls, v):
        if v < 0:
            raise ValueError('Salary must be greater than 0')
        return v

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    staff_code: Optional[str] = None
    doctor_id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    salary: Optional[Decimal] = None
    joining_date: Optional[date] = None
    address: Optional[str] = None
    status: Optional[int] = None

class StaffResponse(StaffBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True