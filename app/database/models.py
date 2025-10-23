"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func

from .database import Base


class BookingDB(Base):
    """Booking database model"""
    
    __tablename__ = "bookings"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    user_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    service = Column(String, nullable=False)
    date = Column(String, nullable=False, index=True)  # ISO format: YYYY-MM-DD
    time = Column(String, nullable=False)  # HH:MM format
    duration_minutes = Column(Integer, default=60)
    status = Column(String, default="confirmed", index=True)  # confirmed, cancelled, pending
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "phone": self.phone,
            "service": self.service,
            "date": self.date,
            "time": self.time,
            "duration_minutes": self.duration_minutes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
