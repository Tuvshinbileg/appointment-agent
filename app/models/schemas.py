"""
Pydantic models for request/response validation
"""
from typing import Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Incoming chat message from user"""
    message: str = Field(..., description="User's message", example="Маргааш 10:00-д үс засалт захиалмаар байна")
    user_id: Optional[str] = Field(default="default_user", description="User identifier", example="user_123")
    session_id: Optional[str] = Field(default=None, description="Session identifier for conversation tracking", example="session_abc123")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Маргааш 10:00-д үс засалт захиалмаар байна",
                "user_id": "user_123",
                "session_id": "session_abc123"
            }
        }


class ChatResponse(BaseModel):
    """Response from the chat agent"""
    response: str = Field(..., description="Agent's response in Mongolian", example="Би шалгаж байна... Тэр цагт сул байна. Таны нэр болон утасны дугаар?")
    booking_id: Optional[str] = Field(default=None, description="Booking ID if created", example="abc123-def456-ghi789")
    status: str = Field(default="success", description="Response status", example="success")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Баярлалаа! Таны үс засалтын цаг 2025-10-24 10:00-д амжилттай батлагдлаа.",
                "booking_id": "abc123-def456-ghi789",
                "status": "success"
            }
        }


class BookingCreate(BaseModel):
    """Schema for creating a booking"""
    user_id: str = Field(..., description="User identifier", example="user_123")
    user_name: str = Field(..., description="User's full name", example="Батаа")
    phone: str = Field(..., description="Phone number", example="99112233")
    service: str = Field(..., description="Service type", example="үс засалт")
    date: str = Field(..., description="Date in YYYY-MM-DD format", example="2025-10-24")
    time: str = Field(..., description="Time in HH:MM format", example="10:00")
    duration_minutes: Optional[int] = Field(default=None, description="Duration in minutes (optional)", example=60)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "user_name": "Батаа",
                "phone": "99112233",
                "service": "үс засалт",
                "date": "2025-10-24",
                "time": "10:00",
                "duration_minutes": 60
            }
        }


class Booking(BaseModel):
    """Complete booking data structure"""
    id: str = Field(..., description="Unique booking ID", example="abc123-def456-ghi789")
    user_id: str = Field(..., description="User identifier", example="user_123")
    user_name: str = Field(..., description="User's full name", example="Батаа")
    phone: str = Field(..., description="Phone number", example="99112233")
    service: str = Field(..., description="Service type", example="үс засалт")
    date: str = Field(..., description="Date in YYYY-MM-DD format", example="2025-10-24")
    time: str = Field(..., description="Time in HH:MM format", example="10:00")
    duration_minutes: int = Field(default=60, description="Duration in minutes", example=60)
    status: str = Field(default="confirmed", description="Booking status: confirmed, cancelled, or pending", example="confirmed")
    created_at: str = Field(..., description="Creation timestamp", example="2025-10-23T10:00:00")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123-def456-ghi789",
                "user_id": "user_123",
                "user_name": "Батаа",
                "phone": "99112233",
                "service": "үс засалт",
                "date": "2025-10-24",
                "time": "10:00",
                "duration_minutes": 60,
                "status": "confirmed",
                "created_at": "2025-10-23T10:00:00"
            }
        }


class AvailabilityCheck(BaseModel):
    """Schema for checking availability"""
    date: str = Field(..., description="Date in YYYY-MM-DD format", example="2025-10-24")
    time: str = Field(..., description="Time in HH:MM format", example="10:00")
    duration: int = Field(default=60, description="Duration in minutes", example=60)
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-10-24",
                "time": "10:00",
                "duration": 60
            }
        }
