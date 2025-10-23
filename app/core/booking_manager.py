"""
BookingManager - Handles all booking operations and data persistence
Now using SQLAlchemy for database operations (SQLite/PostgreSQL)
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from config import SERVICES, BUSINESS_START_HOUR, BUSINESS_END_HOUR
from app.database import SessionLocal, BookingDB


class BookingManager:
    """Manages all booking operations and data persistence using SQLAlchemy"""
    
    def __init__(self):
        self.services = SERVICES
        self.business_start = BUSINESS_START_HOUR
        self.business_end = BUSINESS_END_HOUR
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def _close_db(self, db: Session):
        """Close database session"""
        db.close()
    
    def check_availability(self, date: str, time: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Check if a time slot is available
        
        Args:
            date: ISO format date (YYYY-MM-DD)
            time: Time in HH:MM format
            duration_minutes: Duration of the appointment
            
        Returns:
            Dict with 'available' boolean and 'conflicts' list
        """
        db = self._get_db()
        try:
            requested_start = datetime.fromisoformat(f"{date}T{time}:00")
            requested_end = requested_start + timedelta(minutes=duration_minutes)
            
            conflicts = []
            
            # Query bookings for the same date that are not cancelled
            bookings = db.query(BookingDB).filter(
                BookingDB.date == date,
                BookingDB.status != 'cancelled'
            ).all()
            
            for booking in bookings:
                booking_start = datetime.fromisoformat(f"{booking.date}T{booking.time}:00")
                booking_end = booking_start + timedelta(minutes=booking.duration_minutes)
                
                # Check for overlap
                if (requested_start < booking_end and requested_end > booking_start):
                    conflicts.append({
                        'booking_id': booking.id,
                        'time': booking.time,
                        'service': booking.service
                    })
            
            return {
                'available': len(conflicts) == 0,
                'conflicts': conflicts
            }
        finally:
            self._close_db(db)
    
    def suggest_alternatives(self, date: str, time: str, duration_minutes: int = 60, count: int = 3) -> List[Dict]:
        """
        Suggest alternative time slots if the requested time is not available
        
        Args:
            date: ISO format date
            time: Time in HH:MM format
            duration_minutes: Duration needed
            count: Number of alternatives to suggest
            
        Returns:
            List of available time slots
        """
        alternatives = []
        requested_dt = datetime.fromisoformat(f"{date}T{time}:00")
        
        # Try times around the requested time (±3 hours)
        for offset in range(-180, 181, 30):  # Check every 30 minutes
            if len(alternatives) >= count:
                break
            
            alt_dt = requested_dt + timedelta(minutes=offset)
            
            # Skip if outside business hours
            if alt_dt.hour < self.business_start or alt_dt.hour >= self.business_end:
                continue
            
            alt_date = alt_dt.strftime('%Y-%m-%d')
            alt_time = alt_dt.strftime('%H:%M')
            
            availability = self.check_availability(alt_date, alt_time, duration_minutes)
            
            if availability['available']:
                alternatives.append({
                    'date': alt_date,
                    'time': alt_time,
                    'datetime': alt_dt.isoformat()
                })
        
        return alternatives
    
    def create_booking(self, user_id: str, user_name: str, phone: str, 
                      service: str, date: str, time: str, 
                      duration_minutes: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a new booking
        
        Args:
            user_id: User identifier
            user_name: User's name
            phone: User's phone number
            service: Type of service
            date: ISO format date
            time: Time in HH:MM format
            duration_minutes: Duration (optional, will use service default)
            
        Returns:
            Dict with booking details or error
        """
        # Determine duration
        if duration_minutes is None:
            duration_minutes = self.services.get(service.lower(), 60)
        
        # Check availability
        availability = self.check_availability(date, time, duration_minutes)
        
        if not availability['available']:
            return {
                'success': False,
                'error': 'time_conflict',
                'conflicts': availability['conflicts'],
                'alternatives': self.suggest_alternatives(date, time, duration_minutes)
            }
        
        db = self._get_db()
        try:
            # Create booking
            booking_id = str(uuid.uuid4())
            booking_db = BookingDB(
                id=booking_id,
                user_id=user_id,
                user_name=user_name,
                phone=phone,
                service=service,
                date=date,
                time=time,
                duration_minutes=duration_minutes,
                status='confirmed'
            )
            
            db.add(booking_db)
            db.commit()
            db.refresh(booking_db)
            
            return {
                'success': True,
                'booking': booking_db.to_dict()
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': f'database_error: {str(e)}'
            }
        finally:
            self._close_db(db)
    
    def cancel_booking(self, booking_id: Optional[str] = None, 
                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel a booking by ID or find user's most recent booking
        
        Args:
            booking_id: Specific booking ID to cancel
            user_id: User ID to find their booking
            
        Returns:
            Dict with cancellation result
        """
        db = self._get_db()
        try:
            if booking_id:
                booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
                if booking:
                    booking.status = 'cancelled'
                    db.commit()
                    db.refresh(booking)
                    return {
                        'success': True,
                        'booking': booking.to_dict()
                    }
                else:
                    return {'success': False, 'error': 'booking_not_found'}
            
            elif user_id:
                # Find user's most recent confirmed booking
                bookings = db.query(BookingDB).filter(
                    BookingDB.user_id == user_id,
                    BookingDB.status == 'confirmed'
                ).order_by(
                    BookingDB.date.desc(),
                    BookingDB.time.desc()
                ).all()
                
                if not bookings:
                    return {'success': False, 'error': 'no_bookings_found'}
                
                latest_booking = bookings[0]
                latest_booking.status = 'cancelled'
                db.commit()
                db.refresh(latest_booking)
                
                return {
                    'success': True,
                    'booking': latest_booking.to_dict()
                }
            
            return {'success': False, 'error': 'insufficient_info'}
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': f'database_error: {str(e)}'}
        finally:
            self._close_db(db)
    
    def list_bookings(self, user_id: Optional[str] = None, 
                     status: Optional[str] = None) -> List[Dict]:
        """
        List bookings with optional filters
        
        Args:
            user_id: Filter by user ID
            status: Filter by status (confirmed, cancelled, etc.)
            
        Returns:
            List of bookings
        """
        db = self._get_db()
        try:
            query = db.query(BookingDB)
            
            if user_id:
                query = query.filter(BookingDB.user_id == user_id)
            
            if status:
                query = query.filter(BookingDB.status == status)
            
            # Sort by date and time
            bookings = query.order_by(BookingDB.date, BookingDB.time).all()
            
            return [booking.to_dict() for booking in bookings]
        finally:
            self._close_db(db)
    
    def get_booking(self, booking_id: str) -> Optional[Dict]:
        """Get a specific booking by ID"""
        db = self._get_db()
        try:
            booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
            return booking.to_dict() if booking else None
        finally:
            self._close_db(db)
