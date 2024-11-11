"""
Rate limiting utilities for the frontend application.
"""
from datetime import datetime, timedelta
import streamlit as st
from typing import Optional
from .config import get_settings
from .exceptions import RateLimitError

def check_rate_limit(guest_mode: bool = True) -> bool:
    """
    Check if the current session is within rate limits.
    
    Args:
        guest_mode: Whether the user is in guest mode
        
    Returns:
        bool: True if within rate limit, False otherwise
    """
    settings = get_settings()
    current_time = datetime.utcnow()
    
    # Initialize rate limit state if needed
    if "rate_limit_start" not in st.session_state:
        st.session_state.rate_limit_start = current_time
        st.session_state.questions_used = 0
    
    # Check if we need to reset the window
    window_hours = settings.RATE_LIMIT_WINDOW_HOURS
    if current_time - st.session_state.rate_limit_start > timedelta(hours=window_hours):
        st.session_state.rate_limit_start = current_time
        st.session_state.questions_used = 0
    
    # Get appropriate limit based on auth status
    limit = (settings.AUTHENTICATED_RATE_LIMIT 
             if not guest_mode 
             else settings.ANONYMOUS_RATE_LIMIT)
    
    return st.session_state.questions_used < limit

def increment_rate_limit():
    """
    Increment the rate limit counter.
    
    Raises:
        RateLimitError: If rate limit would be exceeded
    """
    if not check_rate_limit(st.session_state.get("guest_mode", True)):
        raise RateLimitError("Rate limit exceeded. Please try again later.")
    
    st.session_state.questions_used += 1

def get_rate_limit_reset_time() -> Optional[datetime]:
    """
    Get the time when the rate limit will reset.
    
    Returns:
        Optional[datetime]: Time when rate limit will reset, or None if not set
    """
    if "rate_limit_start" in st.session_state:
        settings = get_settings()
        return (st.session_state.rate_limit_start + 
                timedelta(hours=settings.RATE_LIMIT_WINDOW_HOURS))
    return None

def format_rate_limit_message() -> str:
    """
    Get a formatted message about rate limit status.
    
    Returns:
        str: Formatted rate limit message
    """
    settings = get_settings()
    questions_used = st.session_state.get("questions_used", 0)
    guest_mode = st.session_state.get("guest_mode", True)
    
    limit = (settings.AUTHENTICATED_RATE_LIMIT 
             if not guest_mode 
             else settings.ANONYMOUS_RATE_LIMIT)
    
    remaining = limit - questions_used
    
    if reset_time := get_rate_limit_reset_time():
        time_to_reset = reset_time - datetime.utcnow()
        hours = int(time_to_reset.total_seconds() // 3600)
        minutes = int((time_to_reset.total_seconds() % 3600) // 60)
        
        return (f"{remaining} questions remaining. "
                f"Resets in {hours}h {minutes}m")
    
    return f"{remaining} questions remaining"