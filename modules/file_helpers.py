"""
Everything related to handling files (uploads etc)
"""
import streamlit as st
import pandas as pd
from modules.table_info import TableInfo, generate_table_sample_for_system_prompt
from modules.ui_helpers import append_non_user_message

from modules.logger import get_logger
logger = get_logger(__name__)

PROMPT_BASE_TEMPLATE = """
I have {length} tables in database.
{table_samples}
"""

def dedup_files(uploaded_name_to_path):
    """
    Assuming file content is immutable (meaning if a file content changes, its name will change),
    this function refreshes table_info:
        1. if a file is deleted, remove its entry from table_info
        2. add new files
    @return: added
    """
    to_del = []
    for name, item in st.session_state.table_info.items():
        if name not in uploaded_name_to_path:
            to_del.append(name)
    logger.debug("processing uploaded file, deleted files: " + str(to_del))
    for name in to_del:
        del st.session_state.table_info[name]

    added = []
    for name in uploaded_name_to_path:
        if name not in st.session_state.table_info:
            added.append(name)
    logger.debug(f"processing uploaded file, new files: {added}")

    return added


def _process_uploaded_paths(cnx_main, cnx_sample, uploaded_files):
    uploaded_name_to_path = {}
    for path in uploaded_files:
        uploaded_name_to_path[path.name] = path

    added = dedup_files(uploaded_name_to_path)

    if added:
        for name in added:
            df = pd.read_csv(uploaded_name_to_path[name])
            st.session_state.table_info[name] = TableInfo(name, df, cnx_main, cnx_sample)

        ### TODO: add info about unique & null item
        table_samples = generate_table_sample_for_system_prompt(st.session_state.table_info)
        append_non_user_message("system", PROMPT_BASE_TEMPLATE.format(length=len(uploaded_files), table_samples=table_samples))

def handle_upload(cnx_main, cnx_sample):
    """
    Handles and display uploaded_file, and save them to db.
    """
    uploaded_files = st.sidebar.file_uploader("upload", accept_multiple_files=True, type="csv",
                                              label_visibility="collapsed")
    num_uploaded_files = len(uploaded_files)
    if num_uploaded_files > 0:
        logger.debug(f"received {num_uploaded_files} uploaded files.")
        with st.spinner("Processing uploaded files. Each new file takes approximately 30s."):
            _process_uploaded_paths(cnx_main, cnx_sample, uploaded_files)
    else:
        st.session_state["reset_chat"] = True