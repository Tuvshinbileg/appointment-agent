"""
Utility functions for parsing dates, times, and text
"""
import re
from datetime import datetime, timedelta
from typing import Optional


def parse_date_mongolian(text: str) -> Optional[str]:
    """
    Parse Mongolian date expressions to ISO format
    
    Examples:
        - "маргааш" -> tomorrow's date
        - "өнөөдөр" -> today's date
        - "2025-10-23" -> 2025-10-23
    
    Args:
        text: Text containing date expression
        
    Returns:
        ISO format date string (YYYY-MM-DD) or None
    """
    text_lower = text.lower()
    today = datetime.now()
    
    if "өнөөдөр" in text_lower:
        return today.strftime('%Y-%m-%d')
    elif "маргааш" in text_lower:
        tomorrow = today + timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')
    elif "нөгөөдөр" in text_lower:
        day_after = today + timedelta(days=2)
        return day_after.strftime('%Y-%m-%d')
    
    # Try to extract ISO date format
    iso_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if iso_match:
        return iso_match.group(0)
    
    return None


def parse_time(text: str) -> Optional[str]:
    """
    Parse time from text
    
    Examples:
        - "10:00" -> "10:00"
        - "14 цаг" -> "14:00"
        - "2 цагт" -> "14:00" (2 PM)
    
    Args:
        text: Text containing time expression
        
    Returns:
        Time string in HH:MM format or None
    """
    # Try HH:MM format
    time_match = re.search(r'(\d{1,2}):(\d{2})', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        return f"{hour:02d}:{minute:02d}"
    
    # Try "X цаг" format
    hour_match = re.search(r'(\d{1,2})\s*цаг', text)
    if hour_match:
        hour = int(hour_match.group(1))
        return f"{hour:02d}:00"
    
    return None


def extract_phone_number(text: str) -> Optional[str]:
    """
    Extract phone number from text
    
    Args:
        text: Text containing phone number
        
    Returns:
        Phone number string or None
    """
    # Mongolian phone numbers are typically 8 digits
    phone_match = re.search(r'\d{8,}', text)
    if phone_match:
        return phone_match.group(0)
    
    return None


def extract_service(text: str, services: dict) -> Optional[str]:
    """
    Extract service type from text
    
    Args:
        text: Text containing service name
        services: Dictionary of available services
        
    Returns:
        Service name or None
    """
    text_lower = text.lower()
    
    for service in services.keys():
        if service in text_lower:
            return service
    
    return None
