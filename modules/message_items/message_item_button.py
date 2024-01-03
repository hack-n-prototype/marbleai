import streamlit as st
from modules.message_items.message_items import MessageItem
from modules.message_items.message_item_user import append_user_item
from modules.constants import PendingQuery

from modules.logger import get_logger
logger = get_logger(__name__)

BUTTON_TEXT_GENERATE_SQL = "Looks good! Help me generate SQL queries!"
GENERATE_SQL_PROMPT = """
Return SQL queries for user query. SQL only, no explanation. 
"""

BUTTON_TEXT_CONFIRM_APPLY_SQL = "Looks good! Apply SQL to my data set!"

# TODO: think about join later
# BUTTON_TEXT_JOIN_DETAILS = "Tell me more about join"
# JOIN_DETAULS_PROMPT = """
# Explain different types of joins in SQL, clarify which one to use and why. Keep answer short, ideally under 300 char.
# """

BUTTON_TEXT_TO_PROMPT = {
    BUTTON_TEXT_GENERATE_SQL: GENERATE_SQL_PROMPT,
    BUTTON_TEXT_CONFIRM_APPLY_SQL: None
}

class MessageItemButton(MessageItem):
    def __init__(self, content, api_content):
        # api_content is:
        #   sql query, if content is BUTTON_TEXT_APPLY_SQL_TO_MAIN_DB
        #   prompt, otherwise
        if api_content is None:
            api_content = BUTTON_TEXT_TO_PROMPT[content]
        super().__init__("button", content, api_content)

    def _send_to_openai(self):
        return False

    def show_on_screen(self):
        if st.button(self.content):
            logger.info(f"button '{self.content}' clicked.")
            if self.content == BUTTON_TEXT_GENERATE_SQL:
                st.session_state.pending_query = (PendingQuery.GENERATE_SQL, None)
            elif self.content == BUTTON_TEXT_CONFIRM_APPLY_SQL:
                st.session_state.pending_query = (PendingQuery.CONFIRM_APPLY_SQL, self._api_content)
            else:
                logger.error(f"Unexpected button: {self.content}")

            append_user_item(self.content, self._api_content)
