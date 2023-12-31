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

    def get_openai_obj(self):
        return {"role": self.role, "content": self.content}

    def show_on_screen(self):
        with st.chat_message(self.role):
            st.markdown(self.content)

class MessageItemSystem(MessageItem):
    def __init__(self, content):
        super().__init__("system", content)

    def show_on_screen(self):
        # Do not show system prompt on screen
        return

class MessageItemAssistant(MessageItem):
    def __init__(self, content):
        super().__init__("assistant", content)

class MessageItemTable(MessageItem):
    def __init__(self, title, df):
        super().__init__("table", str(df.iat[0,0]) if df.shape == (1,1) else df)
        self.title = title

    def get_openai_obj(self):
        return None

    def show_on_screen(self):
        with st.chat_message("assistant"):
            if isinstance(self.content, str):
                st.markdown(f"{self.title}: {self.content}")
                return

            def _show_expander_w_df(title, df):
                with st.expander(title):
                    st.dataframe(df)

            if self.content.shape[0] <= PREVIEW_CSV_ROWS:
                _show_expander_w_df(self.title, self.content)
            else:
                _show_expander_w_df(f"{self.title} (First {PREVIEW_CSV_ROWS} rows)", self.content.head(PREVIEW_CSV_ROWS))
                file_name = f"result_{st.session_state.id}_{generate_random_string(10)}.csv"
                st.download_button(
                    label="Download full result as CSV",
                    data=self.content.to_csv().encode('utf-8'),
                    file_name=file_name,
                    mime='text/csv',
                    key=file_name,
                )
