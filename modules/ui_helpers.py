import streamlit as st
from modules.constants import QUERY_PROMPT_TEMPLATE
from modules.button_helpers import get_query_label_for_button, BUTTON_TEXT_TO_PROMPT

from modules.logger import get_logger
logger = get_logger(__name__)

# TODO: make them enums
MESSAGE_ROLE_USER = "user"
MESSAGE_ROLE_SYSTEM = "system"
MESSAGE_ROLE_ASSISTANT = "assistant"
MESSAGE_ROLE_ACTIONS = "actions"
MESSAGE_ROLE_INFO = "info"

class MessageItem:
    def __init__(self, role, content, api_content):
        self.role = role
        self.content = content
        self.api_content = api_content

    def get_openai_message_obj(self):
        if (self.role == MESSAGE_ROLE_SYSTEM or self.role == MESSAGE_ROLE_USER or self.role == MESSAGE_ROLE_ASSISTANT) and self.api_content:
            return {"role": self.role, "content": self.api_content }
        else:
            return None

    def show_on_screen(self):
        if self.role == MESSAGE_ROLE_SYSTEM:
            return
        elif self.role == MESSAGE_ROLE_ACTIONS:
            for button in self.content:
                if st.button(button):
                    logger.info(f"button '{button}' clicked.")
                    st.session_state.pending_query_label = get_query_label_for_button(button)
                    append_user_message("action", button)
        elif self.role == MESSAGE_ROLE_USER or self.role == MESSAGE_ROLE_ASSISTANT:
            with st.chat_message(self.role):
                st.markdown(self.content)
        elif self.role == MESSAGE_ROLE_INFO:
            with st.chat_message(self.role):
                st.markdown(self.content)
        else:
            logger.error(f"Unexpected message role: {self.role}")

def _is_last_message_actions(messages):
    return len(messages) > 0 and messages[-1].role == "actions"

def append_user_message(label, content): # Do not name as "type", it shadows system function
    rerun = False # Rerun after (1) appending buttons or (2) removing buttons

    if label == "query":
        api_content = QUERY_PROMPT_TEMPLATE.format(query=content)
    elif label == "action":
        api_content = BUTTON_TEXT_TO_PROMPT[content]
        rerun = True
    else:
        logger.error("Unkonwn user message type")
        return None

    if _is_last_message_actions(st.session_state.messages):
        st.session_state.messages.pop()
        rerun = True

    item = _update_chat_history("user", content, api_content)

    if rerun:
        st.rerun()

    return item


def append_non_user_message(role, content):
    return  _update_chat_history(role, content, content)

def _update_chat_history(role, content, api_content):
    item = MessageItem(role, content, api_content)
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

