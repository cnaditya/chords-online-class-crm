from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    template_id = Column(Integer, nullable=False)
    template_name = Column(String(100))
    phone_number = Column(String(15), nullable=False)
    variables = Column(JSON)  # Store template variables as JSON
    status = Column(String(20), default="pending")  # pending, sent, failed
    response_data = Column(JSON)  # Store API response
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    sent_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", backref="notification_logs")