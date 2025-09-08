from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    file_path = Column(String(500))
    file_type = Column(String(50))  # video, audio, pdf, image
    file_size = Column(Integer)
    lesson_number = Column(Integer)
    instructor = Column(String(50), nullable=False)
    is_public = Column(Boolean, default=False)  # If true, visible to all students of instructor
    access_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="materials")
    enrollment = relationship("Enrollment", backref="materials")