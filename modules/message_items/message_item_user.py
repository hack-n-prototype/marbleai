import streamlit as st
import pandas as pd
pd.set_option('display.max_columns', None)

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

    def get_openai_message_obj(self):
        return None if self.prompt is None else {"role": "user", "content": self.prompt}


def _remove_tailing_buttons():
    removed = False
    while len(st.session_state.messages) > 0 and st.session_state.messages[-1].role == "button":
        st.session_state.messages.pop()
        removed = True
    return removed

def append_user_item_for_query_type(content, query_type):
    if query_type == "SQL":
        prompt = QUERY_PROMPT_TEMPLATE.format(query=content)
    else:
        df = st.session_state.df
        prompt = f"""I have a list of pandas.dataframe "df"\n"""
        for idx, item in enumerate(df):
            prompt += f"df[{idx}]:\n{item.head(3)}\n"
        prompt += f"""
User asks: {content}
Return full and executable python code that converts data frame "df" to figure "fig" via Plotly. Data is clean and well-formatted, plotly is installed. Do not call fig.show(). Keep answer short, ideally under 300 char.  
        """
    return append_user_item(content, prompt)

def append_user_item(content, prompt):
    rerun = _remove_tailing_buttons()
    item = MessageItemUser(content, prompt)
    st.session_state.messages.append(item)

    if rerun:
        st.rerun()
    return item
