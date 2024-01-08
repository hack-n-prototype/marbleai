import os
import streamlit as st
from modules import utils
from modules import file_helpers
from modules import query_helpers
from modules.constants import PREVIEW_CSV_ROWS, PendingQuery
from modules.message_items.utils import  append_non_user_message, append_table_item
from modules.message_items.message_item_button import BUTTON_TEXT_CONFIRM_APPLY_SQL
from modules.message_items.message_item_user import append_user_item
from modules import login
import pandas as pd
import openai
import sqlite3

from modules.logger import get_logger
logger = get_logger(__name__)

def setup_session():
    st.set_page_config(layout="wide", page_icon="💬", page_title="Marble | Chat-Bot 🤖")

    if "id" not in st.session_state:
        st.session_state.id = utils.generate_random_string(length=10)
    st.session_state.setdefault("user_email", None)
    st.session_state.setdefault("table_preview", [])
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("pending_query", None)

    st.markdown(
        "<h1 style='text-align: center;'> Ask Marble about your CSV files! </h1>",
        unsafe_allow_html=True,
    )

    # Init openai key
    if not os.getenv('OPENAI_API_KEY'):
        os.environ["OPENAI_API_KEY"] = st.secrets["openai_secret_key"]
    openai.api_key = os.getenv('OPENAI_API_KEY')

def run_sql_on_main(sql):
    df = pd.read_sql_query(sql, cnx_main)
    append_table_item(f"SQL result on full data set", df).show_on_screen()

##########################
# main
##########################
setup_session()
login.ask_for_user_email()
cnx_main = sqlite3.connect(f"/tmp/{st.session_state.id}.db")
cnx_sample = sqlite3.connect(f"/tmp/{st.session_state.id}_sample.db")
file_helpers.handle_upload(cnx_main, cnx_sample)

if st.session_state.table_preview:
    # Show table preview
    for name, sample in st.session_state.table_preview:
        with st.expander(f"{name} -- first {PREVIEW_CSV_ROWS} rows"):
            st.dataframe(sample)
    # Show chat
    for message in st.session_state.messages:
        message.show_on_screen()

    # Show user input box
    if prompt := st.chat_input("e-g : How many rows ? "):
        logger.info(f"user_input: {prompt}")
        st.session_state.pending_query = (PendingQuery.QUERY, prompt)
        # Query is handled separately, because rerun() from append_user_item may interrupt processing
        append_user_item(prompt).show_on_screen()

    if st.session_state.pending_query:
        pending_query = st.session_state.pending_query
        logger.info(f"handling pending_query: {pending_query}")
        if pending_query[0] == PendingQuery.CONFIRM_APPLY_SQL:
            run_sql_on_main(pending_query[1])
        elif pending_query[0] == PendingQuery.QUERY:
            res, follow_ups = query_helpers.query_openai_w_stream()
            append_non_user_message("assistant", res)
            if sql:= utils.extract_code_from_string(res):
                logger.debug(f"executing sql on sample: {sql}")
                df = pd.read_sql_query(sql, cnx_sample)
                append_table_item(f"SQL result on sample data (first {PREVIEW_CSV_ROWS} rows of each file)", df).show_on_screen()
                append_non_user_message("button", BUTTON_TEXT_CONFIRM_APPLY_SQL, sql).show_on_screen()
            for follow_up in follow_ups:
                append_non_user_message("button", follow_up).show_on_screen()

        st.session_state.pending_query = None # Putting it at the bottom bc this will trigger a rerun