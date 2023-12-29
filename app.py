import os
import importlib
import sys
import streamlit as st
from modules import utils
from modules import file_helpers
from modules import query_helpers
from modules.ui_helpers import update_chat_history
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
    if "id" not in st.session_state:
        st.session_state.id = utils.generate_random_string(length=10)
    st.session_state.setdefault("reset_chat", False)
    st.session_state.setdefault("table_info", {})
    st.session_state.setdefault("prompt_base", None)
    st.session_state.setdefault("user_query", None)
    st.session_state.setdefault("button_clicked", None)
    st.session_state.setdefault("messages", [])

    st.set_page_config(layout="wide", page_icon="💬", page_title="Marble | Chat-Bot 🤖")
    st.markdown(
        "<h1 style='text-align: center;'> Ask Marble about your CSV files ! 😁</h1>",
        unsafe_allow_html=True,
    )

    # Init openai key
    if not os.getenv('OPENAI_API_KEY'):
        os.environ["OPENAI_API_KEY"] = st.secrets["openai_secret_key"]
    openai.api_key = os.getenv('OPENAI_API_KEY')


setup_session()

cnx = sqlite3.connect(f"/tmp/{st.session_state.id}.db")
file_helpers.handle_upload(cnx)

if st.session_state.table_info:
    # Show table preview
    for name, item in st.session_state.table_info.items():
        with st.expander(f"{name} sample"):
            st.dataframe(item.original_sample)
    # Show chat
    for message in st.session_state.messages:
        message.show_on_screen()

    # Show user input box and its handler
    if prompt := st.chat_input("e-g : How many rows ? "):
        st.session_state.user_query = prompt
        update_chat_history("user", prompt).show_on_screen()
        res, actions = query_helpers.answer_user_query()
        update_chat_history("assistant", res)
        update_chat_history("actions",  actions).show_on_screen()

    # Handle button clicked
    if st.session_state.button_clicked:
        logger.debug(f"handling button '{st.session_state.button_clicked}' clicked event.")
        arr = query_helpers.handle_button_click(st.session_state.button_clicked)
        st.session_state.button_clicked = None
        for i in arr:
            if i[0] == "sql":
                sql_res = str(cnx.cursor().execute(i[1]).fetchall())
                update_chat_history("assistant", sql_res).show_on_screen()
            elif i[0] == "actions":
                update_chat_history(i[0], i[1]).show_on_screen()
            elif i[0] == "assistant":
                # No need to show_on_screen bc the response is streaming'ed
                update_chat_history(i[0], i[1])
            else:
                logger.error(f"Exception: unexpected type {i[0]}")
