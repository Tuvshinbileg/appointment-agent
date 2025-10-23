"""
FastAPI route handlers
"""
from typing import Optional
from fastapi import APIRouter, HTTPException

from app.models import ChatMessage, ChatResponse, BookingCreate
from app.core import BookingManager, ChatAgent

# Initialize router
router = APIRouter()

# These will be initialized in main.py
booking_manager: Optional[BookingManager] = None
chat_agent: Optional[ChatAgent] = None


def init_routes(bm: BookingManager, ca: ChatAgent):
    """Initialize the route dependencies"""
    global booking_manager, chat_agent
    booking_manager = bm
    chat_agent = ca


@router.get(
    "/",
    tags=["General"],
    summary="API Information",
    description="Get API version, status, and available endpoints"
)
async def root():
    """Root endpoint with API information"""
    llm_provider = chat_agent.provider.upper() if chat_agent else "Unknown"
    llm_model = chat_agent.model if chat_agent else "Unknown"
    
    return {
        "message": "Appointment Booking Chat Agent API",
        "status": "running",
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "bookings": "/bookings",
            "availability": "/availability",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Chat with Booking Agent",
    description="""
    Send a message to the AI booking assistant. The agent can:
    - Understand natural language in Mongolian
    - Create new bookings
    - Check availability
    - Cancel bookings
    - Suggest alternative times
    
    **Example messages:**
    - "Маргааш 10:00-д үс засалт захиалмаар байна" (I want to book a haircut tomorrow at 10:00)
    - "Миний захиалгуудыг харуулаарай" (Show my bookings)
    - "Захиалга цуцлаарай" (Cancel booking)
    """
)
async def chat_endpoint(message: ChatMessage):
    """
    Main chat endpoint for conversational booking
    
    Args:
        message: ChatMessage with user's message and metadata
        
    Returns:
        ChatResponse with agent's response
    """
    if not chat_agent:
        raise HTTPException(status_code=500, detail="Chat agent not initialized")
    
    try:
        response = chat_agent.process_message(
            message.message,
            user_id=message.user_id,
            session_id=message.session_id
        )
        return ChatResponse(response=response, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/bookings",
    tags=["Bookings"],
    summary="List Bookings",
    description="Get a list of all bookings with optional filters by user_id or status (confirmed/cancelled)"
)
async def list_bookings(
    user_id: Optional[str] = None,
    status: Optional[str] = None
):
    """
    List all bookings with optional filters
    
    Args:
        user_id: Filter by user ID
        status: Filter by booking status (confirmed, cancelled)
        
    Returns:
        Dict with bookings list and count
    """
    if not booking_manager:
        raise HTTPException(status_code=500, detail="Booking manager not initialized")
    
    bookings = booking_manager.list_bookings(user_id=user_id, status=status)
    return {"bookings": bookings, "count": len(bookings)}


@router.get(
    "/bookings/{booking_id}",
    tags=["Bookings"],
    summary="Get Booking by ID",
    description="Retrieve detailed information about a specific booking using its unique ID"
)
async def get_booking(booking_id: str):
    """
    Get a specific booking by ID
    
    Args:
        booking_id: Booking ID
        
    Returns:
        Booking details
    """
    if not booking_manager:
        raise HTTPException(status_code=500, detail="Booking manager not initialized")
    
    booking = booking_manager.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post(
    "/bookings",
    tags=["Bookings"],
    summary="Create Booking (Direct)",
    description="""
    Create a new booking directly without using the chat interface.
    
    **Note:** This bypasses the conversational AI and creates the booking immediately.
    All fields are required except duration_minutes (defaults to service duration).
    """,
    status_code=201
)
async def create_booking_direct(booking: BookingCreate):
    """
    Create a booking directly without chat
    
    Args:
        booking: BookingCreate with all required fields
        
    Returns:
        Created booking details
    """
    if not booking_manager:
        raise HTTPException(status_code=500, detail="Booking manager not initialized")
    
    result = booking_manager.create_booking(
        user_id=booking.user_id,
        user_name=booking.user_name,
        phone=booking.phone,
        service=booking.service,
        date=booking.date,
        time=booking.time,
        duration_minutes=booking.duration_minutes
    )
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result['booking']


@router.delete(
    "/bookings/{booking_id}",
    tags=["Bookings"],
    summary="Cancel Booking",
    description="Cancel a specific booking by its ID. The booking status will be updated to 'cancelled'"
)
async def cancel_booking_endpoint(booking_id: str):
    """
    Cancel a booking by ID
    
    Args:
        booking_id: Booking ID to cancel
        
    Returns:
        Cancelled booking details
    """
    if not booking_manager:
        raise HTTPException(status_code=500, detail="Booking manager not initialized")
    
    result = booking_manager.cancel_booking(booking_id=booking_id)
    if not result['success']:
        raise HTTPException(status_code=404, detail="Booking not found")
    return result['booking']


@router.get(
    "/availability",
    tags=["Availability"],
    summary="Check Availability",
    description="""
    Check if a specific time slot is available for booking.
    
    **Parameters:**
    - date: YYYY-MM-DD format (e.g., 2025-10-24)
    - time: HH:MM format (e.g., 10:00)
    - duration: Duration in minutes (default: 60)
    
    **Returns:**
    - available: boolean
    - conflicts: list of conflicting bookings (if any)
    - alternatives: suggested alternative times (if unavailable)
    """
)
async def check_availability(
    date: str,
    time: str,
    duration: int = 60
):
    """
    Check if a time slot is available
    
    Args:
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format
        duration: Duration in minutes
        
    Returns:
        Availability information with alternatives if unavailable
    """
    if not booking_manager:
        raise HTTPException(status_code=500, detail="Booking manager not initialized")
    
    result = booking_manager.check_availability(date, time, duration)
    
    if not result['available']:
        alternatives = booking_manager.suggest_alternatives(date, time, duration)
        result['alternatives'] = alternatives
    
    return result


@router.delete(
    "/clear-session/{session_id}",
    tags=["Chat"],
    summary="Clear Session History",
    description="Clear the conversation history for a specific chat session. This resets the AI's context."
)
async def clear_session(session_id: str):
    """
    Clear conversation history for a session
    
    Args:
        session_id: Session ID to clear
        
    Returns:
        Success message
    """
    if not chat_agent:
        raise HTTPException(status_code=500, detail="Chat agent not initialized")
    
    chat_agent.clear_history(session_id)
    return {"message": "Session cleared", "session_id": session_id}


@router.get(
    "/health",
    tags=["General"],
    summary="Health Check",
    description="Check the health status of the API and its components"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "booking_manager": booking_manager is not None,
        "chat_agent": chat_agent is not None,
        "database": "connected"
    }
