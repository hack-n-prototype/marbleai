import streamlit as st

from modules.message_items.message_items import MessageItem

QUERY_PROMPT_TEMPLATE = """
User ask: {query}
Explain SQL steps to answer user query. Don't provide SQL queries. Data is clean and well-formatted. Keep answer short, ideally under 300 char.
"""

class MessageItemUser(MessageItem):
    def __init__(self, content, prompt=None):
        super().__init__("user", content)
        # prompt = None -> self.prompt = None
        # prompt = "" -> generate self.prompt from content
        # prompt is a string -> keep it
        self.prompt = QUERY_PROMPT_TEMPLATE.format(query=content) if prompt == "" else prompt

    def _get_api_prompt(self):
        return self.prompt
    def _send_to_openai(self):
        # Some user messages are derived from button
        return self.prompt is not None


def _remove_tailing_buttons():
    removed = False
    while len(st.session_state.messages) > 0 and st.session_state.messages[-1].role == "button":
        st.session_state.messages.pop()
        removed = True
    return removed

def append_user_item(content, prompt=""):
    rerun = _remove_tailing_buttons()
    item = MessageItemUser(content, prompt)
    st.session_state.messages.append(item)

    if rerun:
        st.rerun()
    return item
