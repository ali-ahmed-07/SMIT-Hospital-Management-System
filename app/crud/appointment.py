from sqlalchemy.orm import Session, joinedload
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.staff import Staff
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from typing import Optional
from datetime import date, time, timedelta, datetime

def generate_appointment_code(db: Session) -> str:
    """Generate a unique appointment code"""
    last_appointment = db.query(Appointment).order_by(Appointment.id.desc()).first()
    next_num = (last_appointment.id + 1) if last_appointment else 1
    return f"APT-{next_num:04d}"

def get_appointment(db: Session, appointment_id: int):
    """Get a single appointment with all related data"""
    return db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor),
        joinedload(Appointment.staff)
    ).filter(Appointment.id == appointment_id).first()

def get_appointment_by_code(db: Session, appointment_code: str):
    """Get appointment by code"""
    return db.query(Appointment).filter(Appointment.appointment_code == appointment_code).first()

def get_appointments(db: Session, skip: int = 0, limit: int = 100, 
                      patient_id: Optional[int] = None, 
                      doctor_id: Optional[int] = None,
                      status: Optional[str] = None,
                      date_from: Optional[date] = None,
                      date_to: Optional[date] = None):
    """Get appointments with filters"""
    query = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor),
        joinedload(Appointment.staff)
    )
    
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if status:
        query = query.filter(Appointment.status == status)
    if date_from:
        query = query.filter(Appointment.appointment_date >= date_from)
    if date_to:
        query = query.filter(Appointment.appointment_date <= date_to)
    
    return query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).offset(skip).limit(limit).all()

def get_appointments_with_details(db: Session, skip: int = 0, limit: int = 100):
    """Get appointments with patient, doctor, and staff details for listing"""
    return db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor),
        joinedload(Appointment.staff)
    ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).offset(skip).limit(limit).all()

def create_appointment(db: Session, appointment: AppointmentCreate):
    """Create a new appointment"""
    # Generate appointment code
    appointment_code = generate_appointment_code(db)
    
    # Create appointment
    db_appointment = Appointment(
        appointment_code=appointment_code,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        staff_id=appointment.staff_id,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        reason=appointment.reason,
        symptoms=appointment.symptoms,
        notes=appointment.notes,
        status=appointment.status,
        follow_up_date=appointment.follow_up_date,
        follow_up_notes=appointment.follow_up_notes
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def update_appointment(db: Session, appointment_id: int, appointment: AppointmentUpdate):
    """Update an appointment"""
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment:
        update_data = appointment.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_appointment, key, value)
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int):
    """Delete an appointment"""
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment:
        db.delete(db_appointment)
        db.commit()
        return True
    return False

def update_appointment_status(db: Session, appointment_id: int, status: str):
    """Update appointment status"""
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment:
        db_appointment.status = status
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

def get_appointments_by_patient(db: Session, patient_id: int, status: Optional[str] = None):
    """Get all appointments for a specific patient"""
    query = db.query(Appointment).filter(Appointment.patient_id == patient_id)
    if status:
        query = query.filter(Appointment.status == status)
    return query.order_by(Appointment.appointment_date.desc()).all()

def get_appointments_by_doctor(db: Session, doctor_id: int, appointment_date: Optional[date] = None):
    """Get all appointments for a specific doctor"""
    query = db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
    if appointment_date:
        query = query.filter(Appointment.appointment_date == appointment_date)
    return query.order_by(Appointment.appointment_time).all()

def get_today_appointments(db: Session):
    """Get today's appointments"""
    today = date.today()
    return db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor)
    ).filter(Appointment.appointment_date == today).order_by(Appointment.appointment_time).all()

def get_upcoming_appointments(db: Session, days: int = 7):
    """Get upcoming appointments"""
    today = date.today()
    future_date = today + timedelta(days=days)
    return db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor)
    ).filter(
        Appointment.appointment_date >= today,
        Appointment.appointment_date <= future_date,
        Appointment.status.in_(["scheduled", "confirmed"])
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()

def check_appointment_conflict(db: Session, doctor_id: int, appointment_date: date, appointment_time: time, exclude_id: Optional[int] = None):
    """Check if there's a conflict for doctor's schedule"""
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status.in_(["scheduled", "confirmed", "in-progress"])
    )
    if exclude_id:
        query = query.filter(Appointment.id != exclude_id)
    return query.first() is not None