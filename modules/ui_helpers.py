import streamlit as st

from modules.logger import get_logger
logger = get_logger(__name__)

class MessageItem:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def show_on_screen(self):
        if self.role == "actions":
            for button in self.content:
                if st.button(button):
                    logger.info(f"button '{button}' clicked.")
                    st.session_state.button_clicked = button
                    update_chat_history("user", button)
                    st.rerun()
        else:
            with st.chat_message(self.role):
                st.markdown(self.content)

def _is_last_message_actions(messages):
    return len(messages) > 0 and messages[-1].role == "actions"

def update_chat_history(role, content):
    if _is_last_message_actions(st.session_state.messages):
        st.session_state.messages.pop()
    item = MessageItem(role, content)
    st.session_state.messages.append(item)
    return item

def update_chat_stream(result):
    message_placeholder = st.empty()
    full_response = ""
    for response in result:
        if response["choices"][0].delta:
            full_response += (response["choices"][0].delta.content or "")
        else:
            full_response += ""
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response
