from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from typing import Optional, List

def get_doctor(db: Session, doctor_id: int):
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()

def get_doctor_by_code(db: Session, doctor_code: str):
    return db.query(Doctor).filter(Doctor.doctor_code == doctor_code).first()

def get_doctors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Doctor).offset(skip).limit(limit).all()

def generate_doctor_code(db: Session) -> str:
    last_doctor = db.query(Doctor).order_by(Doctor.id.desc()).first()
    next_num = (last_doctor.id + 1) if last_doctor else 1
    code = f"DOC-{next_num:04d}"

    # Safety check agar id gaps ki wajah se code already exist ho
    while get_doctor_by_code(db, code):
        next_num += 1
        code = f"DOC-{next_num:04d}"
    return code

def create_doctor(db: Session, doctor: DoctorCreate):
    db_doctor = Doctor(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def update_doctor(db: Session, doctor_id: int, doctor: DoctorUpdate):
    db_doctor = get_doctor(db, doctor_id)
    if db_doctor:
        for key, value in doctor.dict(exclude_unset=True).items():
            setattr(db_doctor, key, value)
        db.commit()
        db.refresh(db_doctor)
    return db_doctor

def delete_doctor(db: Session, doctor_id: int):
    db_doctor = get_doctor(db, doctor_id)
    if db_doctor:
        db.delete(db_doctor)
        db.commit()
        return True
    return False

def toggle_status(db: Session, doctor_id: int):
    db_doctor = get_doctor(db, doctor_id)
    if db_doctor:
        db_doctor.status = 0 if db_doctor.status == 1 else 1
        db.commit()
        db.refresh(db_doctor)
    return db_doctor