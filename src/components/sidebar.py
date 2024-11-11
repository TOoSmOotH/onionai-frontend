"""
Sidebar component for navigation and controls.
"""
import streamlit as st
from utils.session import get_chat_history
from components.authentication import AuthenticationManager

class Sidebar:
    """
    Handles the sidebar interface including authentication and chat history.
    """
    def __init__(self):
        self.auth_manager = AuthenticationManager()

    def render(self):
        """Render the sidebar interface."""
        with st.sidebar:
            self._render_auth_section()
            
            if self.auth_manager.is_authenticated():
                self._render_chat_history()
            
            self._render_settings()
            self._render_about()

    def _render_auth_section(self):
        """Render authentication section."""
        st.sidebar.title("Account")
        
        if self.auth_manager.is_authenticated():
            username = self.auth_manager.get_username()
            st.sidebar.success(f"Logged in as {username}")
            self.auth_manager.render_logout_ui()
        else:
            self.auth_manager.render_login_ui()

    def _render_chat_history(self):
        """Render chat history section for authenticated users."""
        st.sidebar.title("Chat History")
        
        history = get_chat_history()
        if history:
            for session in history:
                if st.sidebar.button(
                    f"Chat {session['created_at'][:10]}",
                    key=session['session_id']
                ):
                    st.session_state.messages = session['messages']
                    st.session_state.session_id = session['session_id']
                    st.experimental_rerun()
        else:
            st.sidebar.info("No previous chats found")

    def _render_settings(self):
        """Render settings section."""
        st.sidebar.title("Settings")
        
        # Theme selector
        theme = st.sidebar.selectbox(
            "Theme",
            options=["Light", "Dark"],
            key="theme_setting"
        )
        
        # Apply theme
        if theme == "Dark":
            st.markdown("""
                <style>
                    .stApp {
                        background-color: #1a1a1a;
                        color: #ffffff;
                    }
                </style>
                """, unsafe_allow_html=True)

    def _render_about(self):
        """Render about section."""
        st.sidebar.title("About")
        st.sidebar.info(
            "AI Chat Platform - A powerful chat interface "
            "powered by advanced AI. Use it to ask questions, "
            "get assistance, and explore ideas."
        )