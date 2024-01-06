import os
import streamlit as st
from modules import utils
from modules import file_helpers
from modules import query_helpers
from modules.constants import PREVIEW_CSV_ROWS, PendingQuery
from modules.message_items.utils import  append_non_user_message, append_table_item
from modules.message_items.message_item_button import BUTTON_TEXT_CONFIRM_APPLY_SQL, BUTTON_TEXT_GENERATE_SQL
from modules.message_items.message_item_user import append_user_item, append_user_item_for_query_type
from modules import login
import pandas as pd
import openai
import sqlite3
import plotly
from modules import query_type

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
    st.session_state.setdefault("df", [])

    st.markdown(
        "<h1 style='text-align: center;'> Ask Marble about your CSV files! </h1>",
        unsafe_allow_html=True,
    )

    # Init openai key
    if not os.getenv('OPENAI_API_KEY'):
        os.environ["OPENAI_API_KEY"] = st.secrets["openai_secret_key"]
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # keep the order -- this needs openapi_api_key
    if "query_type_vector_db" not in st.session_state:
        query_type.init()

def handle_generate_sql():
    status = ["Generating SQL and applying it to sample data..."]
    with st.status(status[-1]):
        sql_status, sql = query_helpers.query_sql_w_status()
        status.extend(sql_status)
        df = pd.read_sql_query(sql, cnx_sample)
        status.append("Done!")
        st.write(status[-1])
    append_non_user_message("status", status, sql)
    append_table_item(f"SQL result on sample data (first {PREVIEW_CSV_ROWS} rows of each file)", df).show_on_screen()
    append_non_user_message("button", BUTTON_TEXT_CONFIRM_APPLY_SQL, sql).show_on_screen()

def run_sql_on_main(sql):
    df = pd.read_sql_query(sql, cnx_main)
    st.session_state.df.append(df)
    append_table_item(f"(First {PREVIEW_CSV_ROWS} rows of) SQL result on full data set", df).show_on_screen()

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
        if query_type.get_query_type(prompt) == query_type.SQL:
            st.session_state.pending_query = (PendingQuery.QUERY_SQL, None)
            append_user_item_for_query_type(prompt, query_type.SQL).show_on_screen()
        else:
            st.session_state.pending_query = (PendingQuery.QUERY_GRAPH, None)
        # Query is handled separately, because rerun() from append_user_item may interrupt processing
            append_user_item_for_query_type(prompt, query_type.GRAPH).show_on_screen()

    if st.session_state.pending_query:
        pending_query = st.session_state.pending_query
        logger.info(f"handling pending_query: {pending_query}")
        if pending_query[0] == PendingQuery.GENERATE_SQL:
            handle_generate_sql()
        elif pending_query[0] == PendingQuery.CONFIRM_APPLY_SQL:
            run_sql_on_main(pending_query[1])
        elif pending_query[0] == PendingQuery.QUERY_SQL:
            res = query_helpers.query_openai(True)
            append_non_user_message("assistant", res)
            append_non_user_message("button", BUTTON_TEXT_GENERATE_SQL).show_on_screen()
        elif pending_query[0] == PendingQuery.QUERY_GRAPH:
            res = query_helpers.query_openai(True)
            append_non_user_message("assistant", res)
            code = utils.extract_code_from_string(res)
            print(code)
            df = st.session_state.df
            exec(code)
            st.plotly_chart(fig)
        st.session_state.pending_query = None # Putting it at the bottom bc this will trigger a rerun