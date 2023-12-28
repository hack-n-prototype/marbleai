"""
Everything related to handling files (uploads etc)
"""
import streamlit as st
import pandas as pd
from modules import utils
from modules import constants
from modules import table_info

from modules.logger import get_logger
logger = get_logger(__name__)

PROMPT_BASE_TEMPLATE = """
I have {length} tables in database.
{table_samples}
"""

def refresh_cleanup_script(uploaded):
    """
    This function refreshes table_info:
        1. first remove any out-dated entries from table_info
        2. if a file exists in uploaded but not table_info, add it
    @return: added
    TODO: we should hash-sum the entire file
    """

    # Delete files with out-dated schema
    to_del = []
    for name, item in st.session_state.table_info.items():
        if (name not in uploaded) or (str(uploaded[name].head(constants.PREVIEW_CSV_ROWS)) != str(item.original_sample)):
            to_del.append(name)
    logger.debug("processing uploaded file, out-dated files: " + str(to_del))
    for name in to_del:
        del st.session_state.table_info[name]

    added = []
    for name in uploaded:
        # TODO: add name to added if hash sum doesn't match (maning file has changed)
        if name not in st.session_state.table_info:
            added.append(name)
            original_sample = uploaded[name].head(constants.PREVIEW_CSV_ROWS)
            st.session_state.table_info[name] = table_info.TableInfo(utils.convert_to_lowercase(name), original_sample)

    logger.debug("processing uploaded file, new or updated files: " + str(added))
    return added

def handle_upload(cnx):
    """
    Handles and display uploaded_file, and save them to db.
    """
    uploaded_files = st.sidebar.file_uploader("upload", accept_multiple_files=True, type="csv",
                                              label_visibility="collapsed")

    if uploaded_files is not None:
        uploaded = {}
        for path in uploaded_files:
           uploaded[path.name] = pd.read_csv(path)

        added = refresh_cleanup_script(uploaded)

        # TODO: we may want to rerun the script on all files (and re-save them to db) in case user refresh.
        if added:
            ## TODO:hash sum the entire file
            for name in added:
                item = st.session_state.table_info[name]
                formatted_df = item.format_df_and_update_formatted_sample(uploaded[name])
                if formatted_df is None:
                    return

                formatted_df.to_sql(name=item.table_name, con=cnx, index=False, if_exists='replace')

            st.session_state.prompt_base = PROMPT_BASE_TEMPLATE.format(length=len(st.session_state.table_info), table_samples=table_info.format_table_info_dict(st.session_state.table_info))
            table_info.print_table_info_dict(st.session_state.table_info)
            ### TODO: add info about unique & null item
    else:
        st.session_state["reset_chat"] = True


