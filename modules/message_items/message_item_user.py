import streamlit as st

from modules.message_items.message_items import MessageItem

QUERY_PROMPT_TEMPLATE = """
User ask: {query}
Explain SQL steps to answer user query. Don't provide SQL queries. Data is clean and well-formatted. Keep answer short, ideally under 300 char.
"""

class MessageItemUser(MessageItem):
    def __init__(self, content, api_content):
        super().__init__("user", content, api_content)

    def _send_to_openai(self):
        # Some user messages are derived from button
        return self._api_content is not None


def _remove_tailing_buttons():
    removed = False
    while len(st.session_state.messages) > 0 and st.session_state.messages[-1].role == "button":
        st.session_state.messages.pop()
        removed = True
    return removed

def append_user_item(content, api_content=None):
    if api_content is None:
        api_content = QUERY_PROMPT_TEMPLATE.format(query=content)

    rerun = _remove_tailing_buttons()
    item = MessageItemUser(content, api_content)
    st.session_state.messages.append(item)

    if rerun:
        st.rerun()
    return item
