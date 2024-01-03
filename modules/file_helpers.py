"""
Everything related to handling files (uploads etc.)
"""
import streamlit as st
import pandas as pd
from modules.table_info import TableInfo, generate_table_sample_for_system_prompt
from modules.message_items.utils import append_non_user_message

from modules.logger import get_logger
logger = get_logger(__name__)

PROMPT_BASE_TEMPLATE = """
I have {length} tables in database.
{table_samples}
"""

def _process_uploaded_paths(cnx_main, cnx_sample, uploaded_files):
    for path in uploaded_files:
        filename = path.name
        df = pd.read_csv(path)
        st.session_state.table_info[filename] = TableInfo(filename, df, cnx_main, cnx_sample)

    ### TODO: add info about unique & null item
    table_samples = generate_table_sample_for_system_prompt(st.session_state.table_info)
    prompt_base = PROMPT_BASE_TEMPLATE.format(length=len(uploaded_files), table_samples=table_samples)
    append_non_user_message("system", prompt_base)
    logger.debug(f"prompt base: {prompt_base}")


def handle_upload(cnx_main, cnx_sample):
    """
    Handles and display uploaded_file, and save them to db.
    """
    if not st.session_state.table_info:
        upload_form = st.empty()
        with upload_form.form("upload_form"):
            uploaded_files = st.file_uploader("upload", key=st.session_state.id, accept_multiple_files=True, type="csv",
                                              label_visibility="collapsed")
            uploaded = st.form_submit_button("Upload")

        if uploaded and len(uploaded_files) > 0:
            upload_form.empty()
            logger.info(f"received {len(uploaded_files)} uploaded files.")
            with st.spinner("Processing uploaded files. Each new file takes approximately 30s."):
                _process_uploaded_paths(cnx_main, cnx_sample, uploaded_files)

