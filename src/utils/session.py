"""
Session management utilities for the frontend application.
"""
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import streamlit as st
from .config import get_settings

def initialize_session_state():
    """Initialize or reset the session state with default values."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.questions_used = 0
        st.session_state.last_reset_time = datetime.utcnow()
        st.session_state.guest_mode = True

def get_session_id() -> str:
    """
    Get the current session ID.
    
    Returns:
        str: Current session ID
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def reset_session():
    """Reset the current chat session."""
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.questions_used = 0
    st.session_state.last_reset_time = datetime.utcnow()

def get_chat_history() -> List[Dict]:
    """
    Get chat history for the current user.
    
    Returns:
        List[Dict]: List of chat sessions
    """
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    return st.session_state.chat_history

def add_message_to_history(message: Dict):
    """
    Add a message to the current chat history.
    
    Args:
        message: Message to add to history
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append(message)

def get_current_messages() -> List[Dict]:
    """
    Get messages from the current chat session.
    
    Returns:
        List[Dict]: Current chat messages
    """
    return st.session_state.get("messages", [])

def is_rate_limited() -> bool:
    """
    Check if the current session is rate limited.
    
    Returns:
        bool: True if rate limited
    """
    settings = get_settings()
    questions_used = st.session_state.get("questions_used", 0)
    limit = (settings.AUTHENTICATED_RATE_LIMIT 
             if not st.session_state.get("guest_mode") 
             else settings.ANONYMOUS_RATE_LIMIT)
    return questions_used >= limit

def increment_question_count():
    """Increment the question counter for rate limiting."""
    if "questions_used" not in st.session_state:
        st.session_state.questions_used = 0
    st.session_state.questions_used += 1

def get_remaining_questions() -> int:
    """
    Get remaining questions for the current time window.
    
    Returns:
        int: Number of remaining questions
    """
    settings = get_settings()
    questions_used = st.session_state.get("questions_used", 0)
    limit = (settings.AUTHENTICATED_RATE_LIMIT 
             if not st.session_state.get("guest_mode") 
             else settings.ANONYMOUS_RATE_LIMIT)
    return max(0, limit - questions_used)

def set_session_metadata(metadata: Dict):
    """
    Set metadata for the current session.
    
    Args:
        metadata: Session metadata
    """
    if "metadata" not in st.session_state:
        st.session_state.metadata = {}
    st.session_state.metadata.update(metadata)

def get_session_metadata() -> Dict:
    """
    Get metadata for the current session.
    
    Returns:
        Dict: Session metadata
    """
    return st.session_state.get("metadata", {})