from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class BillItemBase(BaseModel):
    description: str
    quantity: float = 1
    unit_price: float = 0.0


class BillItemCreate(BillItemBase):
    pass


class BillItemResponse(BillItemBase):
    id: int
    amount: float

    class Config:
        from_attributes = True


class BillBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    bill_date: date
    discount_percent: float = 0.0
    tax_percent: float = 0.0
    paid_amount: float = 0.0
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class BillCreate(BillBase):
    items: List[BillItemCreate]


class BillUpdate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    appointment_id: Optional[int] = None
    bill_date: Optional[date] = None
    discount_percent: Optional[float] = None
    tax_percent: Optional[float] = None
    paid_amount: Optional[float] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[BillItemCreate]] = None


class BillResponse(BillBase):
    id: int
    bill_code: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    due_amount: float
    payment_status: str
    items: List[BillItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
