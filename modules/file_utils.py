"""
Everything related to handling files (uploads etc)
"""
import streamlit as st
import pandas as pd
from modules import utils
from langchain.callbacks import get_openai_callback
import openai
from modules import constants

from modules.logger import get_logger
logger = get_logger(__name__)


CSV_FORMAT_SYSTEM_PROMPT = "You help users format CSV."
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

PROMPT_BASE_TEMPLATE = """
I have {length} tables in database.
{table_samples}
"""
SINGLE_TABLE_SAMPLE_TEMPLATAE = """
table name: {name}
{sample_data}
"""


TMP_PATH_TEMPLATE = "/tmp/{name}"

def get_script_to_cleanup_csv(name, sample):
    return """print("hello")"""
    path = TMP_PATH_TEMPLATE.format(name=name)

    prompt = CSV_FORMAT_PROMPT_TEMPLATE.format(path=path, sample=sample)

    with get_openai_callback() as cb:
        response = openai.ChatCompletion.create(
            model=constants.MODEL,
            messages=[{"role": "system", "content": CSV_FORMAT_SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}],
            temperature=0)
    logger.debug(cb)

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
table_info[name]: {
    table_name: str
    script: str -- script is based on path /tmp/name
    original_sample: df
    formatted_sample: df
}
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
    for name in st.session_state.table_info:
        if (name not in uploaded) or (str(uploaded[name].head(constants.PREVIEW_CSV_ROWS)) != str(st.session_state.table_info[name]["original_sample"])):
            to_del.append(name)
    logger.debug("to_del: " + str(to_del))
    for name in to_del:
        del st.session_state.table_info[name]

    added = []
    for name in uploaded:
        # TODO: add name to added if hash sum doesn't match (maning file has changed)
        if name not in st.session_state.table_info:
            added.append(name)
            original_sample = uploaded[name].head(constants.PREVIEW_CSV_ROWS)
            script = get_script_to_cleanup_csv(name, original_sample)
            st.session_state.table_info[name] = {
                "table_name": utils.convert_to_lowercase(name),
                "script": script,
                "original_sample": original_sample,
                "formatted_sample": None
            }

    logger.debug("added: " + str(added))
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

        # TODO: we may want to rerun the script on all files (and re-save them to db) in case user refresh.
        if added:
            ## TODO:hash sum the entire file
            for name in added:
                table_info_item = st.session_state.table_info[name]
                try:
                    # formatted_df = exec_cleanup_script(name, uploaded[name], table_info_item["script"])
                    formatted_df = uploaded[name]
                except Exception as e:
                    logger.error(f"Cannot cleanup CSV: {e}")
                    return
                else:
                    formatted_df.to_sql(name=table_info_item["table_name"], con=cnx, index=False, if_exists='replace')
                    st.session_state.table_info[name]["formatted_sample"] = formatted_df.head(constants.PREVIEW_CSV_ROWS)

            table_sample = "\n".join([SINGLE_TABLE_SAMPLE_TEMPLATAE.format(name=item["table_name"], sample_data=item["formatted_sample"]) for item in st.session_state.table_info.values()])
            st.session_state.prompt_base = PROMPT_BASE_TEMPLATE.format(length=len(st.session_state.table_info), table_samples=table_sample)
            ### TODO: add info about unique & null item
    else:
        st.session_state["reset_chat"] = True


