#!/usr/bin/env python3
"""
Appointment Booking Chat Agent - Main Entry Point

Usage:
    python main.py          # Run FastAPI server
    python main.py cli      # Run CLI mode
"""

import sys
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import (
    API_HOST,
    API_PORT,
    API_RELOAD,
    CORS_ORIGINS,
    APP_TITLE,
    APP_DESCRIPTION,
    APP_VERSION
)
from app import BookingManager, ChatAgent, router, init_routes
from app.database import init_db


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Initialize database
    init_db()
    
    # Create FastAPI app with comprehensive metadata
    app = FastAPI(
        title=APP_TITLE,
        description="""
        ## AI-Powered Appointment Booking System
        
        This API provides a complete booking management system with:
        
        ### Features
        - 🤖 **AI Chat Agent** - Natural language booking in Mongolian
        - 📅 **Booking Management** - Create, view, and cancel appointments
        - ⏰ **Availability Checking** - Real-time slot availability
        - 💾 **Database Storage** - SQLite with PostgreSQL support
        - 🔄 **Alternative Suggestions** - Smart rescheduling recommendations
        
        ### Available Services
        - үс засалт (Haircut) - 60 min
        - шүдний үзлэг (Dental Checkup) - 45 min
        - массаж (Massage) - 90 min
        - маникюр (Manicure) - 45 min
        - педикюр (Pedicure) - 60 min
        - косметик (Cosmetics) - 120 min
        
        ### Getting Started
        1. Use `/chat` endpoint for conversational booking
        2. Or use direct `/bookings` endpoints for programmatic access
        3. Check `/availability` before creating bookings
        
        ### Authentication
        Currently no authentication required (add JWT for production)
        """,
        version=APP_VERSION,
        contact={
            "name": "AI Booking Team",
            "email": "support@booking.example.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_tags=[
            {
                "name": "General",
                "description": "General API information and health checks"
            },
            {
                "name": "Chat",
                "description": "Conversational AI booking assistant endpoints"
            },
            {
                "name": "Bookings",
                "description": "Direct booking management operations (CRUD)"
            },
            {
                "name": "Availability",
                "description": "Check time slot availability and get suggestions"
            }
        ],
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize managers
    booking_manager = BookingManager()
    chat_agent = ChatAgent(booking_manager)
    
    # Initialize routes with dependencies
    init_routes(booking_manager, chat_agent)
    
    # Include router
    app.include_router(router)
    
    return app


def run_cli():
    """Run in CLI mode for testing"""
    print("\n" + "="*70)
    print("🤖 APPOINTMENT BOOKING CHAT AGENT - CLI MODE")
    print("="*70)
    print("Type 'exit' to quit")
    print("Type 'clear' to reset conversation")
    print("Type 'bookings' to see your bookings")
    print("="*70 + "\n")
    
    # Initialize database
    init_db()
    
    # Initialize managers
    booking_manager = BookingManager()
    chat_agent = ChatAgent(booking_manager)
    
    user_id = "cli_user"
    session_id = str(uuid.uuid4())
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                chat_agent.clear_history(session_id)
                session_id = str(uuid.uuid4())
                print("🔄 Conversation cleared!\n")
                continue
            
            if user_input.lower() == 'bookings':
                bookings = booking_manager.list_bookings(user_id=user_id)
                print(f"\n📋 Your bookings ({len(bookings)}):")
                for b in bookings:
                    status_emoji = "✅" if b['status'] == 'confirmed' else "❌"
                    print(f"  {status_emoji} {b['service']} - {b['date']} {b['time']} [{b['status']}]")
                print()
                continue
            
            print("🤖 Agent: ", end="", flush=True)
            response = chat_agent.process_message(user_input, user_id, session_id)
            print(response + "\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def run_server():
    """Run FastAPI server"""
    print("\n" + "="*70)
    print("🚀 APPOINTMENT BOOKING CHAT AGENT - API MODE")
    print("="*70)
    print(f"🌐 Server: http://{API_HOST}:{API_PORT}")
    print(f"📚 API Docs: http://{API_HOST}:{API_PORT}/docs")
    print(f"📖 ReDoc: http://{API_HOST}:{API_PORT}/redoc")
    print("="*70)
    print("\nPress Ctrl+C to stop\n")
    
    app = create_app()
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=API_RELOAD, log_level="info")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Run in CLI mode
        run_cli()
    else:
        # Run FastAPI server
        run_server()
