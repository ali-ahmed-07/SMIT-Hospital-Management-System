from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class PrescriptionBase(BaseModel):
    patient_id: int
    doctor_id: int
    diagnosis: str
    medicines: Optional[str] = None
    dosage_instructions: Optional[str] = None
    notes: Optional[str] = None
    prescription_date: date
    valid_until: Optional[date] = None
    is_active: bool = True
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionUpdate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    diagnosis: Optional[str] = None
    medicines: Optional[str] = None
    dosage_instructions: Optional[str] = None
    notes: Optional[str] = None
    prescription_date: Optional[date] = None
    valid_until: Optional[date] = None
    is_active: Optional[bool] = None
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None

class PrescriptionResponse(PrescriptionBase):
    id: int
    prescription_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PrescriptionListResponse(BaseModel):
    id: int
    prescription_code: str
    patient_name: str
    doctor_name: str
    diagnosis: str
    prescription_date: date
    is_active: bool
    created_at: datetime