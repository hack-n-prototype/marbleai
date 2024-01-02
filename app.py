import os
import streamlit as st
from modules import utils
from modules import file_helpers
from modules import query_helpers
from modules.constants import PREVIEW_CSV_ROWS, PendingQuery, HandleQueryOption
from modules.message_items.utils import  append_non_user_message
from modules.message_items.message_item_button import BUTTON_TEXT_CONFIRM_APPLY_SQL
from modules.message_items.message_item_user import append_user_item
import openai
import sqlite3

from modules.logger import get_logger
logger = get_logger(__name__)

def setup_session():
    if "id" not in st.session_state:
        st.session_state.id = utils.generate_random_string(length=10)
    st.session_state.setdefault("table_info", {})
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("pending_query", None)

    st.markdown(
        "<h1 style='text-align: center;'> Ask Marble about your CSV files! </h1>",
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Reset Conversation"):
        st.session_state.table_info = {}
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.session_state.id = utils.generate_random_string(length=10)
        st.rerun()

    st.sidebar.markdown("Please ensure file names are updated to reflect any changes in content for accurate deduplication.")

    # Init openai key
    if not os.getenv('OPENAI_API_KEY'):
        os.environ["OPENAI_API_KEY"] = st.secrets["openai_secret_key"]
    openai.api_key = os.getenv('OPENAI_API_KEY')


def ask_for_user_email():
    st.session_state.setdefault("user_email", None)
    if st.session_state.user_email:
        return

    st.session_state.user_email = st.text_input("Your email or name: ")
    if not st.session_state.user_email:
        st.stop()
    else:
        st.rerun()

def run_sql_on_sample(sql):
    append_non_user_message("info", f"Applying `{sql}` on sample data (first {PREVIEW_CSV_ROWS} rows)...").show_on_screen()
    sample_res = utils.format_sqlite3_cursor(cnx_sample.cursor().execute(sql).fetchall())
    append_non_user_message("info", f"Result is: {sample_res}").show_on_screen()
    append_non_user_message("button", BUTTON_TEXT_CONFIRM_APPLY_SQL, sql).show_on_screen()

def run_sql_on_main(sql):
    append_non_user_message("info", "Processing...").show_on_screen()
    sql_res = utils.format_sqlite3_cursor(cnx_main.cursor().execute(sql).fetchall())
    append_non_user_message("info", f"Final result is: {sql_res}").show_on_screen()

##########################
# main
##########################
st.set_page_config(layout="wide", page_icon="💬", page_title="Marble | Chat-Bot 🤖")
# ask_for_user_email()
setup_session()
cnx_main = sqlite3.connect(f"/tmp/{st.session_state.id}.db")
cnx_sample = sqlite3.connect(f"/tmp/{st.session_state.id}_sample.db")
file_helpers.handle_upload(cnx_main, cnx_sample)

if st.session_state.table_info:
    # Show table preview
    for name, item in st.session_state.table_info.items():
        with st.expander(f"{name} -- first {PREVIEW_CSV_ROWS} rows"):
            st.dataframe(item.original_sample)
    # Show chat
    for message in st.session_state.messages:
        message.show_on_screen()

    # Show user input box and its handler
    if prompt := st.chat_input("e-g : How many rows ? "):
        logger.info(f"User input: {prompt}")
        st.session_state.pending_query = (PendingQuery.QUERY, None)
        # Must append_user_message here because rerun() may be triggered
        # Query is handled separately, because rerun() may interrupt processing
        append_user_item(prompt).show_on_screen()

    if st.session_state.pending_query:
        logger.debug(f"handling query: {st.session_state.pending_query}")
        arr = query_helpers.handle_query(st.session_state.pending_query)
        st.session_state.pending_query = None
        for i in arr:
            if i[0] == HandleQueryOption.RUN_SQL_ON_SAMPLE:
                run_sql_on_sample(i[1])
            elif i[0] == HandleQueryOption.RUN_SQL_ON_MAIN:
                run_sql_on_main(i[1])
            elif i[0] == HandleQueryOption.SHOW_BUTTON:
                append_non_user_message("button", i[1]).show_on_screen()
            elif i[0] == HandleQueryOption.SHOW_ASSISTANT_MSG:
                # No need to show_on_screen bc the response is streaming'ed
                append_non_user_message("assistant", i[1])
            else:
                logger.error(f"Exception: unexpected result label {i[0]}")
