"""
API client for interacting with the backend API Gateway.
"""
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException
import streamlit as st
from utils.config import get_settings
from utils.exceptions import APIError, RateLimitError

class APIClient:
    """
    Client for making requests to the backend API.
    
    Handles all communication with the API Gateway including authentication,
    error handling, and retries.
    """
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.API_URL
        self.timeout = 30
        self.max_retries = 3

    def send_message(
        self,
        message: str,
        session_id: str,
        guest_mode: bool = True
    ) -> str:
        """
        Send a chat message to the API and get the response.

        Args:
            message: The user's message
            session_id: Current session identifier
            guest_mode: Whether the user is in guest mode

        Returns:
            str: The AI's response

        Raises:
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded
        """
        endpoint = f"{self.base_url}/chat"
        
        headers = self._get_headers()
        
        payload = {
            "message": message,
            "session_id": session_id,
            "guest_mode": guest_mode
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded. Please try again later.")
                
            response.raise_for_status()
            
            return response.json()["response"]
            
        except RequestException as e:
            if "timeout" in str(e).lower():
                raise APIError("Request timed out. Please try again.")
            raise APIError(f"Failed to send message: {str(e)}")

    def get_chat_history(self, limit: int = 30) -> list:
        """
        Retrieve chat history for authenticated users.

        Args:
            limit: Maximum number of sessions to retrieve

        Returns:
            list: List of chat sessions

        Raises:
            APIError: If the API request fails
        """
        if not st.session_state.get("user_token"):
            return []

        endpoint = f"{self.base_url}/chat/history"
        
        headers = self._get_headers()
        params = {"limit": limit}

        try:
            response = requests.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["sessions"]
            
        except RequestException as e:
            raise APIError(f"Failed to fetch chat history: {str(e)}")

    def report_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any]
    ):
        """
        Report an error to the backend for logging and monitoring.

        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context about the error
        """
        endpoint = f"{self.base_url}/error"
        
        headers = self._get_headers()
        
        payload = {
            "error_type": error_type,
            "error_message": error_message,
            "context": context
        }

        try:
            requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
        except RequestException:
            # Silently fail for error reporting
            pass

    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests including authentication if available.

        Returns:
            Dict[str, str]: Headers for the request
        """
        headers = {
            "Content-Type": "application/json",
            "X-Client-Version": self.settings.CLIENT_VERSION,
            "X-Session-ID": st.session_state.get("session_id", "")
        }

        # Add authentication token if available
        if token := st.session_state.get("user_token"):
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def _handle_response_error(self, response: requests.Response):
        """
        Handle error responses from the API.

        Args:
            response: Response object from the request

        Raises:
            APIError: With appropriate error message
            RateLimitError: If rate limit is exceeded
        """
        try:
            error_data = response.json()
            error_message = error_data.get("message", "Unknown error occurred")
        except ValueError:
            error_message = response.text or "Unknown error occurred"

        if response.status_code == 429:
            raise RateLimitError(error_message)
        elif response.status_code == 401:
            # Clear invalid token
            if "user_token" in st.session_state:
                del st.session_state.user_token
            raise APIError("Authentication failed. Please log in again.")
        else:
            raise APIError(f"API Error: {error_message}")