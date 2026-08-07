from sqlalchemy.orm import Session, joinedload
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from typing import Optional, List

def generate_patient_code(db: Session) -> str:
    last_patient = db.query(Patient).order_by(Patient.id.desc()).first()
    next_num = (last_patient.id + 1) if last_patient else 1
    code = f"PAT-{next_num:04d}"

    # Safety check agar id gaps ki wajah se code already exist ho
    while get_patient_by_code(db, code):
        next_num += 1
        code = f"PAT-{next_num:04d}"
    return code
def get_patient(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_patient_by_code(db: Session, patient_code: str):
    return db.query(Patient).filter(Patient.patient_code == patient_code).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Patient).offset(skip).limit(limit).all()

def get_patients_with_doctor(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Patient).options(joinedload(Patient.doctor)).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: PatientCreate):
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient: PatientUpdate):
    db_patient = get_patient(db, patient_id)
    if db_patient:
        update_data = patient.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_patient, key, value)
        db.commit()
        db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = get_patient(db, patient_id)
    if db_patient:
        db.delete(db_patient)
        db.commit()
        return True
    return False

def toggle_status(db: Session, patient_id: int):
    db_patient = get_patient(db, patient_id)
    if db_patient:
        db_patient.status = 0 if db_patient.status == 1 else 1
        db.commit()
        db.refresh(db_patient)
    return db_patient

def get_patients_by_doctor(db: Session, doctor_id: int):
    return db.query(Patient).filter(Patient.doctor_id == doctor_id).all()