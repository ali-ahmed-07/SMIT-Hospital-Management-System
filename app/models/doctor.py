from sqlalchemy import Column, Integer, String, DECIMAL, Text, Enum, TIMESTAMP, SmallInteger
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship  

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    doctor_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    salary = Column(DECIMAL(10, 2), nullable=False)
    gender = Column(Enum('Male', 'Female', 'Other'), nullable=False)
    address = Column(Text, nullable=True)
    status = Column(SmallInteger, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    bills = relationship("Bill", back_populates="doctor")