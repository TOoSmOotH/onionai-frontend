"""
Input validation utilities for the frontend application.

This module provides comprehensive validation functions for all user inputs,
data sanitization, and format checking. It includes validation for:
- Chat messages
- User credentials
- Session data
- API responses
- HTML content
"""
from typing import Optional, Dict, Any
import re
import uuid
from datetime import datetime
from .exceptions import ValidationError
from .config import get_settings

def validate_message(message: str) -> str:
    """
    Validate and sanitize a chat message.
    
    Args:
        message: Message to validate
        
    Returns:
        str: Sanitized message
        
    Raises:
        ValidationError: If message is invalid
    """
    # Remove leading/trailing whitespace
    message = message.strip()
    
    # Check length
    if not message:
        raise ValidationError("Message cannot be empty")
    if len(message) > 2000:
        raise ValidationError("Message too long (max 2000 characters)")
    
    # Basic XSS prevention
    message = (message
              .replace("<", "&lt;")
              .replace(">", "&gt;"))
    
    # Check for common injection patterns
    dangerous_patterns = [
        r"javascript:",
        r"data:",
        r"vbscript:",
        r"onload=",
        r"onerror=",
        r"onclick=",
        r"eval\(",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            raise ValidationError("Message contains potentially dangerous content")
    
    return message

def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
        
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
        
    # Additional checks
    if len(email) > 254:  # Maximum length per RFC 5321
        return False
        
    local_part = email.split('@')[0]
    if len(local_part) > 64:  # Maximum local-part length
        return False
        
    return True

def validate_password(password: str) -> Optional[str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Optional[str]: Error message if invalid, None if valid
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return "Password must be less than 128 characters long"
    
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character"
    
    # Check for common patterns
    common_patterns = [
        r"password",
        r"123456",
        r"qwerty",
        r"abc123",
        r"admin",
    ]
    
    for pattern in common_patterns:
        if pattern in password.lower():
            return "Password contains common patterns that are too easy to guess"
    
    return None

def sanitize_html(text: str) -> str:
    """
    Sanitize HTML content.
    
    Args:
        text: Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
        
    allowed_tags = {
        'b', 'i', 'u', 'p', 'br', 'ul', 'ol', 'li', 
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div',
        'em', 'strong', 'code', 'pre', 'blockquote'
    }
    
    # Remove potentially dangerous tags
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<iframe.*?</iframe>', '', text, flags=re.DOTALL)
    text = re.sub(r'<object.*?</object>', '', text, flags=re.DOTALL)
    text = re.sub(r'<embed.*?</embed>', '', text, flags=re.DOTALL)
    
    # Parse and filter HTML
    def replace_tag(match):
        tag = match.group(1).lower()
        if tag in allowed_tags:
            return match.group(0)
        return ''
    
    text = re.sub(r'<(/?)(\w+)(?: .*?)?>', lambda m: replace_tag(m), text)
    
    # Remove any remaining potentially dangerous attributes
    dangerous_attributes = [
        'onclick', 'ondblclick', 'onmousedown', 'onmouseover', 'onmouseout',
        'onkeydown', 'onkeypress', 'onkeyup', 'onload', 'onerror', 'onsubmit',
        'style', 'href', 'src'
    ]
    
    for attr in dangerous_attributes:
        text = re.sub(f'{attr}=".*?"', '', text, flags=re.IGNORECASE)
        text = re.sub(f"{attr}='.*?'", '', text, flags=re.IGNORECASE)
    
    return text

def validate_username(username: str) -> Optional[str]:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        Optional[str]: Error message if invalid, None if valid
    """
    if not username:
        return "Username cannot be empty"
    
    if len(username) < 3:
        return "Username must be at least 3 characters long"
    
    if len(username) > 20:
        return "Username must be less than 20 characters"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return "Username can only contain letters, numbers, underscores, and hyphens"
    
    if username.startswith(('-', '_')) or username.endswith(('-', '_')):
        return "Username cannot start or end with special characters"
    
    # Check for common reserved words
    reserved_words = {
        'admin', 'administrator', 'root', 'system', 'moderator',
        'mod', 'support', 'help', 'info', 'service'
    }
    
    if username.lower() in reserved_words:
        return "This username is reserved"
    
    return None

def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not session_id:
        return False
        
    try:
        # Validate UUID format
        uuid.UUID(session_id)
        return True
    except (ValueError, AttributeError, TypeError):
        return False

def validate_api_response(response: Dict[str, Any]) -> bool:
    """
    Validate API response format.
    
    Args:
        response: API response to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If response is invalid
    """
    if not isinstance(response, dict):
        raise ValidationError("API response must be a dictionary")
    
    required_fields = {'status', 'data'}
    if not all(field in response for field in required_fields):
        raise ValidationError("Invalid API response format: missing required fields")
    
    if response['status'] not in {'success', 'error'}:
        raise ValidationError("Invalid status in API response")
    
    if response['status'] == 'error' and 'error' not in response:
        raise ValidationError("Error response must contain error details")
    
    return True

def validate_timestamp(timestamp: str) -> bool:
    """
    Validate timestamp format.
    
    Args:
        timestamp: Timestamp to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.fromisoformat(timestamp)
        return True
    except (ValueError, TypeError):
        return False

def validate_chat_message(message: Dict[str, Any]) -> bool:
    """
    Validate chat message format.
    
    Args:
        message: Chat message to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If message format is invalid
    """
    required_fields = {'content', 'timestamp', 'role'}
    
    if not all(field in message for field in required_fields):
        raise ValidationError("Invalid message format: missing required fields")
    
    if not isinstance(message['content'], str):
        raise ValidationError("Message content must be a string")
    
    if not validate_timestamp(message['timestamp']):
        raise ValidationError("Invalid timestamp format")
    
    if message['role'] not in {'user', 'assistant'}:
        raise ValidationError("Invalid message role")
    
    # Validate content length
    settings = get_settings()
    if len(message['content']) > settings.MAX_MESSAGE_LENGTH:
        raise ValidationError(f"Message exceeds maximum length of {settings.MAX_MESSAGE_LENGTH} characters")
    
    return True

def validate_file_upload(filename: str, content_type: str, size: int) -> Optional[str]:
    """
    Validate file upload parameters.
    
    Args:
        filename: Name of the uploaded file
        content_type: MIME type of the file
        size: Size of the file in bytes
        
    Returns:
        Optional[str]: Error message if invalid, None if valid
    """
    settings = get_settings()
    
    # Check file size
    if size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        return f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB"
    
    # Check file extension
    allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.md'}
    file_ext = os.path.splitext(filename.lower())[1]
    if file_ext not in allowed_extensions:
        return "File type not allowed"
    
    # Check MIME type
    allowed_mime_types = {
        'text/plain',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/markdown'
    }
    
    if content_type not in allowed_mime_types:
        return "Invalid file type"
    
    return None