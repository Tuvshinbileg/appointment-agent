"""
Appointment Booking Chat Agent Application
"""

__version__ = "1.0.0"
__author__ = "AI Booking Team"
__description__ = "AI-powered booking system with Mongolian language support"

from .core import BookingManager, ChatAgent
from .models import ChatMessage, ChatResponse, Booking, BookingCreate
from .api import router, init_routes

__all__ = [
    "BookingManager",
    "ChatAgent",
    "ChatMessage",
    "ChatResponse",
    "Booking",
    "BookingCreate",
    "router",
    "init_routes"
]
