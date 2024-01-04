import streamlit as st
from modules.message_items.message_items import MessageItem
from modules.message_items.message_item_user import append_user_item
from modules.constants import PendingQuery

from modules.logger import get_logger
logger = get_logger(__name__)

BUTTON_TEXT_GENERATE_SQL = "Looks good! Help me generate SQL queries!"
GENERATE_SQL_PROMPT = """
Return SQLite queries for user query. SQLite only, no explanation. 
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
    def __init__(self, content, sql):
        super().__init__("button", content)
        # prompt is:
        #   sql query, if text is BUTTON_TEXT_APPLY_SQL_TO_MAIN_DB
        #   otherwise, BUTTON_TEXT_TO_PROMPT[button_text]
        self.prompt = sql if sql else BUTTON_TEXT_TO_PROMPT[content]

    def _send_to_openai(self):
        return False

    def _get_api_prompt(self):
        return self.prompt

    def show_on_screen(self):
        if st.button(self.content):
            logger.info(f"button '{self.content}' clicked.")
            if self.content == BUTTON_TEXT_GENERATE_SQL:
                st.session_state.pending_query = (PendingQuery.GENERATE_SQL, None)
            elif self.content == BUTTON_TEXT_CONFIRM_APPLY_SQL:
                st.session_state.pending_query = (PendingQuery.CONFIRM_APPLY_SQL, self.prompt)
            else:
                logger.error(f"Unexpected button: {self.content}")

            if self.content == BUTTON_TEXT_CONFIRM_APPLY_SQL:
                append_user_item(self.content, None)
            else:
                append_user_item(self.content, self.prompt)
