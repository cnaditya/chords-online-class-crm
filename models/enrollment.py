from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    package_type = Column(String(50), nullable=False)  # 1_month_8, 3_months_24, etc.
    total_classes = Column(Integer, nullable=False)
    classes_used = Column(Integer, default=0)
    classes_per_week = Column(Integer, default=1)  # 1 or 2
    fee_amount = Column(Numeric(10, 2), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="active")  # active, expired, cancelled
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="enrollments")
    
    @property
    def classes_remaining(self):
        return self.total_classes - self.classes_used
    
    @property
    def package_name(self):
        from config import Config
        return Config.PACKAGES.get(self.package_type, {}).get("name", self.package_type)