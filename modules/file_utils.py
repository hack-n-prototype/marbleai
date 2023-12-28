"""
Everything related to handling files (uploads etc)
"""
import streamlit as st
import pandas as pd
from modules import utils
from langchain.callbacks import get_openai_callback
import openai
from modules import constants
import re

from modules.logger import get_logger
logger = get_logger(__name__)


CSV_FORMAT_SYSTEM_PROMPT = "You help users format CSV to database."
CSV_FORMAT_PROMPT_TEMPLATE = """
I need to cleanup one CSV file so that it can be saved to database. For example:
1. Remove all comma in numbers. 1,234 -> 1234
2. Remove price symbols. $1,234.5 -> 1234.5
3. Convert column head to lower case and replace space with underscore. "Total NTV" -> "total_ntv"

The file is at path "{path}". Here are the first 3 rows: 
{sample}

Return python script to read from path, format the CSV, and write back to the original path.
You are only allowed to use pandas. 
"""
TMP_PATH_TEMPLATE = "/tmp/{name}"

def get_script_to_cleanup_csv(name, sample):
    path = TMP_PATH_TEMPLATE.format(name=name)

    prompt = CSV_FORMAT_PROMPT_TEMPLATE.format(path=path, sample=sample)

    with get_openai_callback() as cb:
        response = openai.ChatCompletion.create(
            model=constants.MODEL,
            messages=[{"role": "system", "content": CSV_FORMAT_SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}])
    print(cb)

    res = response["choices"][0]["message"]["content"]

    code = utils.extract_code_from_string(res)
    return code

def exec_cleanup_script(name, df, script):
    """
    @return: the cleaned data frame
    """
    path = TMP_PATH_TEMPLATE.format(name=name)
    df.to_csv(path, mode="w+")
    exec(script)
    return pd.read_csv(path)


"""
table_info[name]: (sample, script)
"""
def refresh_cleanup_script(uploaded):
    """
    table_info[name]: (sample, script) -- script is operate on path /tmp/name
    This function refreshes table_info:
        1. first remove any out-dated file from table_info
        2. if a file exists in uploaded but not table_info, add it
    @return: added
    TODO: we should hash-sum the entire file
    """

    # Delete files with out-dated schema
    for name in st.session_state.table_info:
        if (name not in uploaded) or (str(uploaded[name].head(constants.PREVIEW_CSV_ROWS)) != st.session_state.table_info[name][0]):
            del st.session_state.table_info[name]

    added = []
    for name in uploaded:
        # TODO: add name to added if hash sum doesn't match (maning file has changed)
        if name not in st.session_state.table_info:
            added.append(name)
            sample = str(uploaded[name].head(constants.PREVIEW_CSV_ROWS))
            script = get_script_to_cleanup_csv(name, sample)
            st.session_state.table_info[name] = (sample, script)

    return added

def handle_upload(cnx):
    """
    Handles and display uploaded_file, and save them to db.
    sample data (for AI prompt) is saved in st.session_state.table_info
    """
    uploaded_files = st.sidebar.file_uploader("upload", accept_multiple_files=True, type="csv",
                                              label_visibility="collapsed")

    if uploaded_files is not None:
        uploaded = {}
        for path in uploaded_files:
           uploaded[path.name] = pd.read_csv(path)

        added = refresh_cleanup_script(uploaded)

        print("******************")
        print("******************")
        print("******************")
        print({
            "added": added,
            "table_info": st.session_state.table_info
        })

        if added:
            ## TODO:hash sum the entire file
            for name in added:
                (sample, script) = st.session_state.table_info[name]
                try:
                    new_df = exec_cleanup_script(name, uploaded[name], script)
                except Exception as e:
                    logger.error(f"Cannot cleanup CSV: {e}")
                    return
                else:
                    new_df.to_sql(name=name, con=cnx, index=False, if_exists='replace')

            table_sample = "\n".join([f"{name}\n{st.session_state.table_info[name][0]}" for name in st.session_state.table_info])
            st.session_state.prompt_base = constants.PROMPT_BASE_TEMPLATE.format(length=len(uploaded), table_samples=table_sample)
            ### TODO: add info about unique & null item
            logger.info(st.session_state.prompt_base)
    else:
        st.session_state["reset_chat"] = True


