import streamlit as st
from modules.message_items.message_items import  MessageItemAssistant, MessageItemStatus, MessageItemSystem, MessageItemTable
from modules.message_items.message_item_button import  MessageItemButton

from modules.logger import get_logger
logger = get_logger(__name__)

def append_non_user_message(role, content, api_content=None):
    if role == "button":  # Only button can have custom api_content
        item = MessageItemButton(content, api_content)
    elif role == "assistant":
        item = MessageItemAssistant(content)
    elif role == "status":
        item = MessageItemStatus(content)
    elif role == "system":
        item = MessageItemSystem(content)

    st.session_state.messages.append(item)
    return item

def append_table_item(title, df):
    item = MessageItemTable(title, df)
    st.session_state.messages.append(item)
    return item