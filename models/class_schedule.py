from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    instructor = Column(String(50), nullable=False)
    class_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(200))  # RRULE format
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled, rescheduled
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="class_schedules")
    enrollment = relationship("Enrollment", backref="class_schedules")