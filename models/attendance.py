from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    class_schedule_id = Column(Integer, ForeignKey("class_schedules.id"))
    class_date = Column(DateTime, nullable=False)
    instructor = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # present, absent, makeup, cancelled
    notes = Column(Text)
    lesson_topic = Column(String(200))
    homework_assigned = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="attendance_records")
    enrollment = relationship("Enrollment", backref="attendance_records")
    class_schedule = relationship("ClassSchedule", backref="attendance_records")