"""
Everything related to handling files (uploads etc.)
"""
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import pandas as pd
from modules.table_info import TableInfo, convert_filename_to_temp_filepath, get_script_to_cleanup_csv, format_df, SINGLE_TABLE_SAMPLE_TEMPLATE
from modules.message_items.utils import append_non_user_message
import concurrent.futures
from modules.logger import get_logger
from modules import utils
from modules.constants import PREVIEW_CSV_ROWS, API_CSV_ROWS
logger = get_logger(__name__)

PROMPT_BASE_TEMPLATE = """
I have {length} tables in database.
{table_samples}
"""
pd.set_option('display.max_columns', None)

def _get_csv_cleanup_script_by_df(file_name, df):
    return file_name, get_script_to_cleanup_csv(convert_filename_to_temp_filepath(file_name), df)

def _get_csv_cleanup_script_by_map(df_map):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit each task to the executor
        futures = [executor.submit(_get_csv_cleanup_script_by_df, file_name, df_map[file_name]) for file_name in df_map]
        # Since logger uses streamlit session id, threads need streamlit context
        for t in executor._threads:
            add_script_run_ctx(t)

    # Wait for all tasks to complete and retrieve results
    return dict([future.result() for future in concurrent.futures.as_completed(futures)])

def _process_uploaded_paths(cnx_main, cnx_sample, uploaded_files):
    df_map = {}
    for path in uploaded_files:
        file_name = path.name
        df_map[file_name] = pd.read_csv(path)

    result = _get_csv_cleanup_script_by_map(df_map)

    table_samples = []
    for file_name, script in result.items():
        table_name = utils.convert_to_lowercase(file_name)
        st.session_state.table_info[file_name] = TableInfo(table_name, df_map[file_name])

        # Execute cleanup script against original df
        formatted_df = format_df(convert_filename_to_temp_filepath(file_name), df_map[file_name], script)
        formatted_sample = formatted_df.head(PREVIEW_CSV_ROWS)

        # Save clean csv to DB
        formatted_df.to_sql(name=table_name, con=cnx_main, index=False, if_exists='replace')
        formatted_sample.to_sql(name=table_name, con=cnx_sample, index=False, if_exists='replace')
        table_samples.append(SINGLE_TABLE_SAMPLE_TEMPLATE.format(name=table_name,
                                                                 sample_data=formatted_sample.head(API_CSV_ROWS)))

    ### TODO: add info about unique & null item
    prompt_base = PROMPT_BASE_TEMPLATE.format(length=len(uploaded_files), table_samples="\n".join(table_samples))
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

