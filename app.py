import os
import streamlit as st
from modules import utils
from modules import file_helpers
from modules import query_helpers
from modules.query_helpers import QUERY_LABEL_QUERY, RESULT_LABEL_SQL, RESULT_LABEL_ASSISTANT, RESULT_LABEL_ACTIONS, RESULT_LABEL_APPLY_SQL
from modules import vector_db
from modules.constants import PREVIEW_CSV_ROWS
from modules import button_helpers
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
    st.session_state.setdefault("pending_query_label", None)
    st.session_state.setdefault("sql", None)

    st.set_page_config(layout="wide", page_icon="💬", page_title="Marble | Chat-Bot 🤖")
    st.markdown(
        "<h1 style='text-align: center;'> Ask Marble about your CSV files! </h1>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("Please ensure file names are updated to reflect any changes in content for accurate deduplication.")

    # Init openai key
    if not os.getenv('OPENAI_API_KEY'):
        os.environ["OPENAI_API_KEY"] = st.secrets["openai_secret_key"]
    openai.api_key = os.getenv('OPENAI_API_KEY')


setup_session()
cnx_main = sqlite3.connect(f"/tmp/{st.session_state.id}.db")
cnx_sample = sqlite3.connect(f"/tmp/{st.session_state.id}_sample.db")
file_helpers.handle_upload(cnx_main, cnx_sample)

# Add buttons to vector db
if "vector_db" not in st.session_state:
    docs, ids = vector_db.create_button_documents()
    st.session_state.vector_db = vector_db.Vectordb(openai.api_key, docs, ids)


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
        st.session_state.pending_query_label = QUERY_LABEL_QUERY
        append_user_message("query", prompt).show_on_screen()
        # User input is handled separately, because rerun() may interrupt query processing if buttons exist before user input box

    if st.session_state.pending_query_label:
        logger.debug(f"handling query: {st.session_state.pending_query_label}")
        arr = query_helpers.handle_query(st.session_state.pending_query_label)
        st.session_state.pending_query_label = None
        for i in arr:
            if i[0] == RESULT_LABEL_SQL:
                sql_query = i[1]
                st.session_state.sql = sql_query
                append_non_user_message("info", f"Applying `{sql_query}` on sample data (first {PREVIEW_CSV_ROWS} rows)...").show_on_screen()
                sample_res = utils.format_sqlite3_cursor(cnx_sample.cursor().execute(sql_query).fetchall())
                append_non_user_message("info", f"Result is: {sample_res}").show_on_screen()
                # TODO
                ### save sql_query to button,
                ### and change pending_query_label to include query context.
                append_non_user_message("actions", [button_helpers.BUTTON_TEXT_APPLY_SQL_TO_MAIN_DB]).show_on_screen()
            elif i[0] == RESULT_LABEL_APPLY_SQL:
                append_non_user_message("info", "Processing...").show_on_screen()
                sql_res = utils.format_sqlite3_cursor(cnx_main.cursor().execute(st.session_state.sql).fetchall())
                append_non_user_message("info", f"Final result is: {sql_res}").show_on_screen()
                # TODO: delete this variable
                st.session_state.sql = None
            elif i[0] == RESULT_LABEL_ACTIONS:
                append_non_user_message(i[0], i[1]).show_on_screen()
            elif i[0] == RESULT_LABEL_ASSISTANT:
                # No need to show_on_screen bc the response is streaming'ed
                append_non_user_message(i[0], i[1])
            else:
                logger.error(f"Exception: unexpected result label {i[0]}")
