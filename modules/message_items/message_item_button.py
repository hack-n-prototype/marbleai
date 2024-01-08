import streamlit as st
from modules.message_items.message_items import MessageItem
from modules.message_items.message_item_user import append_user_item
from modules.constants import PendingQuery

from modules.logger import get_logger
logger = get_logger(__name__)

BUTTON_TEXT_CONFIRM_APPLY_SQL = "Looks good! Apply SQL to my data set!"

class MessageItemButton(MessageItem):
    def __init__(self, content, sql):
        super().__init__("button", content)
        self.pending_query_info = sql if sql else content

    def get_openai_message_obj(self):
        return None

    def show_on_screen(self):
        if st.button(self.content, key=self.content):
            logger.info(f"button '{self.content}' clicked.")
            if self.content == BUTTON_TEXT_CONFIRM_APPLY_SQL:
                st.session_state.pending_query = (PendingQuery.CONFIRM_APPLY_SQL, self.pending_query_info)
                # Do not send BUTTON_TEXT_CONFIRM_APPLY_SQL to openai
                append_user_item(self.content, False)
            else:
                st.session_state.pending_query = (PendingQuery.QUERY, None)
                append_user_item(self.content, True)
