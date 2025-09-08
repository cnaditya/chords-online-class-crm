from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .base import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    country_code = Column(String(5), nullable=False, default="+91")
    phone = Column(String(15), nullable=False)
    date_of_birth = Column(DateTime)
    address = Column(Text)
    instructor = Column(String(50), nullable=False)  # Aditya or Brahmani
    preferred_instrument = Column(String(50))
    skill_level = Column(String(20), default="Beginner")  # Beginner, Intermediate, Advanced
    timezone = Column(String(50), default="Asia/Kolkata")
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def whatsapp_number(self):
        return f"{self.country_code}{self.phone}"