import streamlit as st

from modules.logger import get_logger
logger = get_logger(__name__)
class MessageItem(object):
    def __init__(self, role, content, api_content):
        self.role = role
        self.content = content
        self._api_content = api_content

    def get_openai_message_obj(self):
        if self._send_to_openai():
            return {"role": self.role, "content": self._api_content }
        else:
            return None

    def _send_to_openai(self):
        return True

    def show_on_screen(self):
        with st.chat_message(self.role):
            st.markdown(self.content)

class MessageItemSystem(MessageItem):
    def __init__(self, content):
        super().__init__("system", content, content)

    def show_on_screen(self):
        # Do not show system prompt on screen
        return

class MessageItemAssistant(MessageItem):
    def __init__(self, content):
        super().__init__("assistant", content, content)


class MessageItemInfo(MessageItem):
    def __init__(self, content):
        super().__init__("info", content, None)
    def _send_to_openai(self):
        return False

