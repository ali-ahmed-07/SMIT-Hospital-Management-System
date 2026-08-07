from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, TIMESTAMP, Boolean, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    appointment_code = Column(String(20), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    
    # Appointment Details
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    reason = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Status: scheduled, confirmed, in-progress, completed, cancelled, no-show
    status = Column(String(20), default="scheduled")
    
    # Follow-up
    follow_up_date = Column(Date, nullable=True)
    follow_up_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", backref="appointments")
    doctor = relationship("Doctor", backref="appointments")
    staff = relationship("Staff", backref="appointments")
    bills = relationship("Bill", back_populates="appointment")