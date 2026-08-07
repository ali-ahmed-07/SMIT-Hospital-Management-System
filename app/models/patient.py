from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, SmallInteger, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_code = Column(String(20), unique=True, nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum('Male', 'Female', 'Other'), nullable=False)
    disease = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=True)
    admission_date = Column(Date, nullable=False)
    discharge_date = Column(Date, nullable=True)
    status = Column(SmallInteger, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship with Doctor
    doctor = relationship("Doctor", backref="patients")
    bills = relationship("Bill", back_populates="patient")
