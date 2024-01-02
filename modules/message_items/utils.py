import streamlit as st
from modules.message_items.message_items import  MessageItemAssistant, MessageItemInfo, MessageItemSystem
from modules.message_items.message_item_button import  MessageItemButton

from modules.logger import get_logger
logger = get_logger(__name__)

def append_non_user_message(role, content, api_content=None):
    if role == "button":  # Only button can have custom api_content
        item = MessageItemButton(content, api_content)
    elif role == "assistant":
        item = MessageItemAssistant(content)
    elif role == "info":
        item = MessageItemInfo(content)
    elif role == "system":
        item = MessageItemSystem(content)

    st.session_state.messages.append(item)
    return item


