"""
Analytics service for tracking user interactions and system metrics.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import streamlit as st
from utils.config import get_settings

class AnalyticsService:
    """
    Handles tracking and reporting of user interactions and system metrics.
    """
    def __init__(self):
        self.settings = get_settings()
        self.enabled = self.settings.ENABLE_ANALYTICS
        self.session_id = str(uuid.uuid4())

    def track_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """
        Track a user interaction event.

        Args:
            event_type: Type of event
            data: Event data
            user_id: Optional user identifier
        """
        if not self.enabled:
            return

        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "user_id": user_id or "anonymous",
            "data": data,
            "metadata": {
                "client_version": self.settings.CLIENT_VERSION,
                "platform": "web",
                "user_agent": st.session_state.get("user_agent", "unknown")
            }
        }

        self._send_event(event)

    def track_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any]
    ):
        """
        Track an error event.

        Args:
            error_type: Type of error
            error_message: Error message
            context: Error context
        """
        if not self.enabled:
            return

        error_event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "user_id": st.session_state.get("username", "anonymous"),
            "data": {
                "error_type": error_type,
                "error_message": error_message,
                "context": context
            },
            "metadata": {
                "client_version": self.settings.CLIENT_VERSION,
                "platform": "web",
                "user_agent": st.session_state.get("user_agent", "unknown")
            }
        }

        self._send_event(error_event)

    def _send_event(self, event: Dict[str, Any]):
        """
        Send event to analytics backend.

        Args:
            event: Event data to send
        """
        try:
            # Here you would typically send the event to your analytics backend
            # For now, we'll just print it in debug mode
            if self.settings.DEBUG:
                print(f"Analytics Event: {event}")
        except Exception as e:
            if self.settings.DEBUG:
                print(f"Failed to send analytics event: {str(e)}")