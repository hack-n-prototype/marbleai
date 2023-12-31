import os
import streamlit as st
from modules import utils
from modules import file_helpers
from modules import query_helpers
from modules import vector_db
from modules import button_helpers
from modules.ui_helpers import update_chat_history
from modules.ui_helpers import  append_user_message, append_non_user_message
import openai
import sqlite3

from modules.logger import get_logger
logger = get_logger(__name__)

def setup_session():
    if "id" not in st.session_state:
        st.session_state.id = utils.generate_random_string(length=10)
    # Need to implement reset_chat
    # st.session_state.setdefault("reset_chat", False)
    st.session_state.setdefault("table_info", {})
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("vector_db", None)
    st.session_state.setdefault("button_clicked", None)
    st.session_state.setdefault("has_pending_user_query", False)

    st.set_page_config(layout="wide", page_icon="💬", page_title="Marble | Chat-Bot 🤖")
    st.markdown(
        "<h1 style='text-align: center;'> Ask Marble about your CSV files ! 😁</h1>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("Please ensure file names are updated to reflect any changes in content for accurate deduplication.")

    # Init openai key
    if not os.getenv('OPENAI_API_KEY'):
        os.environ["OPENAI_API_KEY"] = st.secrets["openai_secret_key"]
    openai.api_key = os.getenv('OPENAI_API_KEY')

setup_session()
cnx = sqlite3.connect(f"/tmp/{st.session_state.id}.db")
file_helpers.handle_upload(cnx)

# Add buttons to vector db
if not st.session_state.vector_db:
    docs, ids = vector_db.create_button_documents()
    db = vector_db.Vectordb(openai.api_key, docs, ids)
    st.session_state.vector_db = db

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
        st.session_state.has_pending_user_query = True
        append_user_message("query", prompt).show_on_screen()

    # Handle user input
    # rerun may interrupt user query processing if buttons exist before user input
    # Thus, taking query processing out of text input box handling.
    if st.session_state.has_pending_user_query:
        res, actions = query_helpers.answer_user_query()
        append_non_user_message("assistant", res)
        append_non_user_message("actions",  actions).show_on_screen()
        st.session_state.has_pending_user_query = False

        related_buttons = button_helpers.determine_buttons(st.session_state.vector_db, res)
        update_chat_history("actions", related_buttons).show_on_screen()

    # Handle button clicked
    if st.session_state.button_clicked:
        logger.debug(f"handling button '{st.session_state.button_clicked}' clicked event.")
        arr = query_helpers.handle_button_click(st.session_state.button_clicked)
        st.session_state.button_clicked = None
        for i in arr:
            if i[0] == "sql":
                sql_res = utils.format_sqlite3_cursor(cnx.cursor().execute(i[1]).fetchall())
                append_non_user_message("assistant", sql_res).show_on_screen()
            elif i[0] == "actions":
                append_non_user_message(i[0], i[1]).show_on_screen()
            elif i[0] == "assistant":
                # No need to show_on_screen bc the response is streaming'ed
                append_non_user_message(i[0], i[1])
            else:
                logger.error(f"Exception: unexpected type {i[0]}")
