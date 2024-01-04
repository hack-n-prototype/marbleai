import streamlit as st
import pandas as pd
from modules.utils import generate_random_string
from modules.constants import  PREVIEW_CSV_ROWS

pd.set_option('display.max_columns', None)

from modules.logger import get_logger
logger = get_logger(__name__)
class MessageItem(object):
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def get_openai_message_obj(self):
        if self._send_to_openai():
            return {"role": self.role, "content": self._get_api_prompt()}
        else:
            return None

    def _get_api_prompt(self):
        logger.error("No implementation.")

    def _send_to_openai(self):
        return True

    def show_on_screen(self):
        with st.chat_message(self.role):
            st.markdown(self.content)

class MessageItemSystem(MessageItem):
    def __init__(self, content):
        super().__init__("system", content)

    def _get_api_prompt(self):
        return self.content

    def show_on_screen(self):
        # Do not show system prompt on screen
        return

class MessageItemAssistant(MessageItem):
    def __init__(self, content):
        super().__init__("assistant", content)

    def _get_api_prompt(self):
        return self.content

class MessageItemStatus(MessageItem):
    def __init__(self, content, prompt):
        super().__init__("status", content)
        self.prompt = prompt
    def _send_to_openai(self):
        return self.prompt is not None

    def _get_api_prompt(self):
        return self.prompt

    def show_on_screen(self):
        with st.status(self.content[0]):
            st.write("\n\n".join(self.content[1:]))


class MessageItemTable(MessageItem):
    def __init__(self, title, df):
        super().__init__("table", str(df.iat[0,0]) if df.shape == (1,1) else df)
        self.title = title

    def _send_to_openai(self):
        return False

    def show_on_screen(self):
        if isinstance(self.content, str):
            with st.chat_message("assistant"):
                st.markdown(f"{self.title}: {self.content}")
            return

        st.write(self.title)
        if self.content.shape[0] <= PREVIEW_CSV_ROWS:
            st.dataframe(self.content)
            return

        file_name = f"result_{st.session_state.id}_{generate_random_string(10)}.csv"
        st.dataframe(self.content.head(PREVIEW_CSV_ROWS))
        st.download_button(
            label="Download full result as CSV",
            data=self.content.to_csv().encode('utf-8'),
            file_name=file_name,
            mime='text/csv',
            key=file_name,
        )
