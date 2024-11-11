"""
Custom exceptions for the frontend application.
"""
from typing import Optional, Dict, Any

class ChatAppError(Exception):
    """Base exception for chat application."""
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class APIError(ChatAppError):
    """Raised when API requests fail."""
    pass

class AuthError(ChatAppError):
    """Raised for authentication-related errors."""
    pass

class RateLimitError(ChatAppError):
    """Raised when rate limits are exceeded."""
    pass

class ConfigurationError(ChatAppError):
    """Raised for configuration-related errors."""
    pass

class ValidationError(ChatAppError):
    """Raised for input validation errors."""
    pass

class SessionError(ChatAppError):
    """Raised for session-related errors."""
    pass

def handle_error(error: Exception) -> Dict[str, Any]:
    """
    Convert an exception into a standardized error response.
    
    Args:
        error: Exception to handle
        
    Returns:
        Dict[str, Any]: Standardized error response
    """
    if isinstance(error, ChatAppError):
        response = {
            "error": True,
            "message": error.message,
            "error_code": error.error_code,
            "details": error.details
        }
    else:
        response = {
            "error": True,
            "message": str(error),
            "error_code": "UNKNOWN_ERROR",
            "details": {}
        }
    
    return response