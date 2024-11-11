"""
Authentication management component using AWS Cognito.
"""
from typing import Optional, Dict
import boto3
import streamlit as st
from utils.config import get_settings
from services.cognito import CognitoService

class AuthenticationManager:
    """
    Handles user authentication and session management.
    """
    def __init__(self):
        self.settings = get_settings()
        self.cognito = CognitoService()

    def render_login_ui(self):
        """Render the login/signup interface."""
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Login")

                if submit_button and username and password:
                    try:
                        auth_result = self.cognito.authenticate(username, password)
                        self._handle_successful_auth(auth_result)
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")

        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("Username")
                email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                signup_button = st.form_submit_button("Sign Up")

                if signup_button:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif all([new_username, email, new_password]):
                        try:
                            self.cognito.sign_up(new_username, email, new_password)
                            st.success("Sign up successful! Please check your email for verification.")
                        except Exception as e:
                            st.error(f"Sign up failed: {str(e)}")

    def render_logout_ui(self):
        """Render the logout button and user info."""
        if st.sidebar.button("Logout"):
            self.logout()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return bool(st.session_state.get("user_token"))

    def get_username(self) -> Optional[str]:
        """Get the current user's username."""
        if self.is_authenticated():
            return st.session_state.get("username")
        return None

    def get_token(self) -> Optional[str]:
        """Get the current authentication token."""
        return st.session_state.get("user_token")

    def logout(self):
        """Handle user logout."""
        if "user_token" in st.session_state:
            del st.session_state.user_token
        if "username" in st.session_state:
            del st.session_state.username
        st.experimental_rerun()

    def _handle_successful_auth(self, auth_result: Dict):
        """
        Handle successful authentication response.

        Args:
            auth_result: Authentication result from Cognito
        """
        st.session_state.user_token = auth_result["AccessToken"]
        st.session_state.username = auth_result["Username"]
        st.experimental_rerun()

    def refresh_token(self) -> bool:
        """
        Refresh the authentication token if needed.

        Returns:
            bool: True if token was successfully refreshed
        """
        try:
            refresh_token = st.session_state.get("refresh_token")
            if refresh_token:
                auth_result = self.cognito.refresh_token(refresh_token)
                self._handle_successful_auth(auth_result)
                return True
        except Exception:
            self.logout()
        return False