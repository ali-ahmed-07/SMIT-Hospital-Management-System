from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, SmallInteger, Date, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    staff_code = Column(String(20), unique=True, nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    salary = Column(DECIMAL(10, 2), nullable=False)   
    joining_date = Column(Date, nullable=False)
    address = Column(Text, nullable=True)
    status = Column(SmallInteger, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    doctor = relationship("Doctor", backref="staff_members")