import os
import importlib
import sys
import streamlit as st
from modules import utils
from modules import file_utils
from modules import query_utils
from modules import chat_utils
import openai
import sqlite3

from modules.logger import get_logger
logger = get_logger(__name__)

def reload_module(module_name):
    """For update changes
    made to modules in localhost (press r)"""

    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]


def setup_session():
    def _set_value_if_not_exist(key, func):
        if key not in st.session_state:
            st.session_state[key] = func()

    _set_value_if_not_exist("id", lambda: utils.generate_random_string(length=10))
    _set_value_if_not_exist("chat_history", lambda:[])
    _set_value_if_not_exist("table_info", lambda:{})
    _set_value_if_not_exist("prompt_base", lambda:"")
    _set_value_if_not_exist("user_query",  lambda:"")
    _set_value_if_not_exist("button_clicked", lambda:"")

    st.set_page_config(layout="wide", page_icon="💬", page_title="Robby | Chat-Bot 🤖")
    st.markdown(
        "<h1 style='text-align: center;'> Ask Robby about your CSV files ! 😁</h1>",
        unsafe_allow_html=True,
    )
    st.session_state.setdefault("reset_chat", False)

    # Init openai key
    if not os.getenv('OPENAI_API_KEY'):
        os.environ["OPENAI_API_KEY"] = st.secrets["openai_secret_key"]
    openai.api_key = os.getenv('OPENAI_API_KEY')


setup_session()

cnx = sqlite3.connect(f"/tmp/{st.session_state.id}.db")
file_utils.handle_upload(cnx)

if st.session_state.table_info:

    # Show table preview
    for name in st.session_state.table_info:
        with st.expander(f"{name} sample"):
            st.table(st.session_state.table_info[name][0])

    # Show user input box
    with st.form(key="query"):
        query = st.text_input(
            "Ask questions",
            value="", type="default",
            placeholder="e-g : How many rows ? "
        )
        submitted_query = st.form_submit_button("Submit")
        reset_chat_button = st.form_submit_button("Reset Chat")
        if reset_chat_button:
            st.session_state["chat_history"] = []

    # If user submit a query
    if submitted_query:
        st.session_state.user_query = query
        query_utils.answer_user_query()

    # Handle button click
    # TODO: couldn't figure out sqlite & threads.
    # putting the code here works
    if st.session_state.button_clicked:
        sql = query_utils.handle_button_click(st.session_state.button_clicked)
        st.session_state.button_clicked = ""
        logger.info(sql)
        if sql:
            res = str(cnx.cursor().execute(sql).fetchall())
            chat_utils.update_chat_history(result=res)

    chat_utils.display_chat_history()