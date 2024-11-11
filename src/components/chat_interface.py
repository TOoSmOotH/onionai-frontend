"""
Chat interface component handling message display and input.
"""
from typing import List, Dict, Optional
import streamlit as st
from services.api_client import APIClient
from utils.session import get_session_id
from utils.rate_limit import check_rate_limit

class ChatInterface:
    """
    Handles the chat interface including message display and input.
    """
    def __init__(self):
        self.api_client = APIClient()

    def render(self, guest_mode: bool = False):
        """
        Render the chat interface.

        Args:
            guest_mode: Whether to show limited guest interface
        """
        # Display chat header
        self._render_header(guest_mode)

        # Display message history
        self._display_messages()

        # Chat input
        self._render_chat_input(guest_mode)

    def _render_header(self, guest_mode: bool):
        """Render the chat interface header."""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if guest_mode:
                st.info(f"Questions remaining: {self._get_remaining_questions()}/10")
            else:
                st.info(f"Questions remaining: {self._get_remaining_questions()}/50")
        
        with col2:
            if st.button("New Chat"):
                self._start_new_chat()

    def _display_messages(self):
        """Display chat message history."""
        messages = st.session_state.get("messages", [])
        
        for msg in messages:
            self._render_message(msg)

    def _render_message(self, message: Dict):
        """
        Render a single chat message.

        Args:
            message: Message data including content and role
        """
        role = message["role"]
        content = message["content"]
        
        with st.container():
            if role == "user":
                st.markdown(
                    f"""<div class="chat-message user-message">
                        🧑 {content}
                    </div>""",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""<div class="chat-message assistant-message">
                        🤖 {content}
                    </div>""",
                    unsafe_allow_html=True
                )

    def _render_chat_input(self, guest_mode: bool):
        """
        Render the chat input interface.

        Args:
            guest_mode: Whether to show limited guest interface
        """
        if not check_rate_limit(guest_mode):
            st.warning("Rate limit reached. Please try again later.")
            return

        with st.container():
            if prompt := st.chat_input("Type your message here..."):
                self._handle_user_input(prompt, guest_mode)

    def _handle_user_input(self, prompt: str, guest_mode: bool):
        """
        Handle user input and get AI response.

        Args:
            prompt: User's input message
            guest_mode: Whether in guest mode
        """
        # Add user message to state
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        try:
            # Get AI response
            response = self.api_client.send_message(
                message=prompt,
                session_id=get_session_id(),
                guest_mode=guest_mode
            )

            # Add assistant response to state
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            # Update rate limit counter
            self._update_question_count()
            
            # Trigger rerun to update UI
            st.experimental_rerun()

        except Exception as e:
            st.error(f"Error: {str(e)}")

    def _start_new_chat(self):
        """Start a new chat session."""
        st.session_state.messages = []
        st.session_state.session_id = get_session_id()
        st.experimental_rerun()

    def _get_remaining_questions(self) -> int:
        """Get remaining questions for current time window."""
        used_questions = st.session_state.get("questions_used", 0)
        limit = 50 if not st.session_state.get("guest_mode", True) else 10
        return max(0, limit - used_questions)

    def _update_question_count(self):
        """Update the question counter."""
        if "questions_used" not in st.session_state:
            st.session_state.questions_used = 0
        st.session_state.questions_used += 1