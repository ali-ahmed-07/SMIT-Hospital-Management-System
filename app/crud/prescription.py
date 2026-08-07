from sqlalchemy.orm import Session, joinedload
from app.models.prescription import Prescription
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate
from typing import Optional
from datetime import date, timedelta

def generate_prescription_code(db: Session) -> str:
    """Generate a unique prescription code"""
    last_prescription = db.query(Prescription).order_by(Prescription.id.desc()).first()
    next_num = (last_prescription.id + 1) if last_prescription else 1
    return f"RX-{next_num:04d}"

def get_prescription(db: Session, prescription_id: int):
    """Get a single prescription with all related data"""
    return db.query(Prescription).options(
        joinedload(Prescription.patient),
        joinedload(Prescription.doctor)
    ).filter(Prescription.id == prescription_id).first()

def get_prescription_by_code(db: Session, prescription_code: str):
    """Get prescription by code"""
    return db.query(Prescription).filter(Prescription.prescription_code == prescription_code).first()

def get_prescriptions(db: Session, skip: int = 0, limit: int = 100, 
                      patient_id: Optional[int] = None, 
                      doctor_id: Optional[int] = None,
                      is_active: Optional[bool] = None):
    """Get prescriptions with filters"""
    query = db.query(Prescription).options(
        joinedload(Prescription.patient),
        joinedload(Prescription.doctor)
    )
    
    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Prescription.doctor_id == doctor_id)
    if is_active is not None:
        query = query.filter(Prescription.is_active == is_active)
    
    return query.order_by(Prescription.prescription_date.desc()).offset(skip).limit(limit).all()

def get_prescriptions_with_details(db: Session, skip: int = 0, limit: int = 100):
    """Get prescriptions with patient and doctor details for listing"""
    return db.query(Prescription).options(
        joinedload(Prescription.patient),
        joinedload(Prescription.doctor)
    ).order_by(Prescription.prescription_date.desc()).offset(skip).limit(limit).all()

def create_prescription(db: Session, prescription: PrescriptionCreate):
    """Create a new prescription"""
    # Generate prescription code
    prescription_code = generate_prescription_code(db)
    
    # Create prescription
    db_prescription = Prescription(
        prescription_code=prescription_code,
        patient_id=prescription.patient_id,
        doctor_id=prescription.doctor_id,
        diagnosis=prescription.diagnosis,
        medicines=prescription.medicines,
        dosage_instructions=prescription.dosage_instructions,
        notes=prescription.notes,
        prescription_date=prescription.prescription_date,
        valid_until=prescription.valid_until,
        is_active=prescription.is_active,
        follow_up_date=prescription.follow_up_date,
        follow_up_notes=prescription.follow_up_notes
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def update_prescription(db: Session, prescription_id: int, prescription: PrescriptionUpdate):
    """Update a prescription"""
    db_prescription = get_prescription(db, prescription_id)
    if db_prescription:
        update_data = prescription.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_prescription, key, value)
        db.commit()
        db.refresh(db_prescription)
    return db_prescription

def delete_prescription(db: Session, prescription_id: int):
    """Delete a prescription"""
    db_prescription = get_prescription(db, prescription_id)
    if db_prescription:
        db.delete(db_prescription)
        db.commit()
        return True
    return False

def toggle_prescription_status(db: Session, prescription_id: int):
    """Toggle prescription active status"""
    db_prescription = get_prescription(db, prescription_id)
    if db_prescription:
        db_prescription.is_active = not db_prescription.is_active
        db.commit()
        db.refresh(db_prescription)
    return db_prescription

def get_prescriptions_by_patient(db: Session, patient_id: int, is_active: Optional[bool] = None):
    """Get all prescriptions for a specific patient"""
    query = db.query(Prescription).filter(Prescription.patient_id == patient_id)
    if is_active is not None:
        query = query.filter(Prescription.is_active == is_active)
    return query.order_by(Prescription.prescription_date.desc()).all()

def get_active_prescriptions_for_patient(db: Session, patient_id: int):
    """Get active prescriptions for a patient"""
    return db.query(Prescription).filter(
        Prescription.patient_id == patient_id,
        Prescription.is_active == True
    ).order_by(Prescription.prescription_date.desc()).all()

def get_upcoming_followups(db: Session, days: int = 7):
    """Get prescriptions with upcoming follow-ups"""
    target_date = date.today() + timedelta(days=days)
    return db.query(Prescription).filter(
        Prescription.follow_up_date <= target_date,
        Prescription.follow_up_date >= date.today(),
        Prescription.is_active == True
    ).options(
        joinedload(Prescription.patient),
        joinedload(Prescription.doctor)
    ).all()