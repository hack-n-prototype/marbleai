import streamlit as st
import pandas as pd

from modules.constants import  PREVIEW_CSV_ROWS
pd.set_option('display.max_columns', None)

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


class MessageItemStatus(MessageItem):
    def __init__(self, content):
        super().__init__("status", content, None)
    def _send_to_openai(self):
        return False

    def show_on_screen(self):
        with st.status(self.content[0]):
            st.write("\n\n".join(self.content[1:]))


class MessageItemTable(MessageItem):
    def __init__(self, title, df):
        super().__init__("table", df, None)
        self.title = title

    def _send_to_openai(self):
        return False

    def show_on_screen(self):
        if self.content.shape == (1,1): # Single answer -> just a text message
            with st.chat_message("assistant"):
                st.markdown(f"{self.title}: {self.content.iat[0,0]}")
            return

        st.write(self.title)
        download = self.content.shape[0] > PREVIEW_CSV_ROWS
        if download:
            st.dataframe(self.content.head(PREVIEW_CSV_ROWS))
            st.download_button(
                label="Download full result as CSV",
                data=self.content.to_csv().encode('utf-8'),
                file_name=f'result_{st.session_state.id}.csv',
                mime='text/csv',
            )
        else:
            st.dataframe(self.content)
