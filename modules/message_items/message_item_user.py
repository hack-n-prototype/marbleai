import streamlit as st
from modules.message_items.message_items import MessageItem

class MessageItemUser(MessageItem):
    def __init__(self, content, send_to_openai):
        super().__init__("user", content)
        self.send_to_openai = send_to_openai

    def get_openai_obj(self):
        return {"role": "user", "content": self.content} if self.send_to_openai else None

def _remove_tailing_buttons():
    removed = False
    while len(st.session_state.messages) > 0 and st.session_state.messages[-1].role == "button":
        st.session_state.messages.pop()
        removed = True
    return removed

def append_user_item(content, send_to_openai=True):
    rerun = _remove_tailing_buttons()
    item = MessageItemUser(content, send_to_openai)
    st.session_state.messages.append(item)

    if rerun:
        st.rerun()
    return item