"""
Main entry point for the AI Chat Platform frontend application.
"""
import streamlit as st
from components.authentication import AuthenticationManager
from components.chat_interface import ChatInterface
from components.sidebar import Sidebar
from utils.config import load_config
from utils.session import initialize_session_state

class ChatApplication:
    """
    Main application class that coordinates all frontend components.
    """
    def __init__(self):
        self.config = load_config()
        self.auth_manager = AuthenticationManager()
        self.chat_interface = ChatInterface()
        self.sidebar = Sidebar()

    def setup_page(self):
        """Configure the Streamlit page settings and layout."""
        st.set_page_config(
            page_title="AI Chat Platform",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply custom CSS
        st.markdown("""
            <style>
                .stAlert {
                    padding: 10px;
                    border-radius: 4px;
                }
                .chat-message {
                    padding: 1rem;
                    border-radius: 0.5rem;
                    margin-bottom: 1rem;
                    max-width: 80%;
                }
                .user-message {
                    background-color: #e3f2fd;
                    margin-left: auto;
                }
                .assistant-message {
                    background-color: #f5f5f5;
                    margin-right: auto;
                }
            </style>
        """, unsafe_allow_html=True)

    def run(self):
        """Main application execution flow."""
        self.setup_page()
        initialize_session_state()

        # Render sidebar with authentication and session controls
        self.sidebar.render()

        # Main content area
        st.title("AI Chat Platform")

        # Handle authentication state
        if self.auth_manager.is_authenticated():
            st.success(f"Welcome back, {self.auth_manager.get_username()}")
            self.chat_interface.render()
        else:
            # Show limited chat interface for unauthenticated users
            st.warning("You are in guest mode. Login to access more features.")
            self.chat_interface.render(guest_mode=True)

def main():
    """Application entry point."""
    app = ChatApplication()
    app.run()

if __name__ == "__main__":
    main()