from sqlalchemy.orm import Session, joinedload
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate
from typing import Optional, List

def generate_staff_code(db: Session) -> str:
    """Generate auto-incrementing staff code"""
    last_staff = db.query(Staff).order_by(Staff.id.desc()).first()
    next_num = (last_staff.id + 1) if last_staff else 1
    code = f"STF-{next_num:04d}"

    # Safety check for existing codes
    while get_staff_by_code(db, code):
        next_num += 1
        code = f"STF-{next_num:04d}"
    return code

def get_staff(db: Session, staff_id: int):
    return db.query(Staff).filter(Staff.id == staff_id).first()

def get_staff_by_code(db: Session, staff_code: str):
    return db.query(Staff).filter(Staff.staff_code == staff_code).first()

def get_staff_by_email(db: Session, email: str):
    return db.query(Staff).filter(Staff.email == email).first()

def get_all_staff(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Staff).offset(skip).limit(limit).all()

def get_staff_with_doctor(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Staff).options(joinedload(Staff.doctor)).offset(skip).limit(limit).all()

def create_staff(db: Session, staff: StaffCreate):
    db_staff = Staff(**staff.model_dump())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

def update_staff(db: Session, staff_id: int, staff: StaffUpdate):
    db_staff = get_staff(db, staff_id)
    if db_staff:
        update_data = staff.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_staff, key, value)
        db.commit()
        db.refresh(db_staff)
    return db_staff

def delete_staff(db: Session, staff_id: int):
    db_staff = get_staff(db, staff_id)
    if db_staff:
        db.delete(db_staff)
        db.commit()
        return True
    return False

def toggle_staff_status(db: Session, staff_id: int):
    db_staff = get_staff(db, staff_id)
    if db_staff:
        db_staff.status = 0 if db_staff.status == 1 else 1
        db.commit()
        db.refresh(db_staff)
    return db_staff

def get_staff_by_doctor(db: Session, doctor_id: int):
    return db.query(Staff).filter(Staff.doctor_id == doctor_id).all()

def get_staff_by_department(db: Session, department: str):
    return db.query(Staff).filter(Staff.department == department).all()