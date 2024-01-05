"""
Everything related to handling files (uploads, cleanup etc.)
"""
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import pandas as pd
from modules.message_items.utils import append_non_user_message
import concurrent.futures
from modules import utils
from modules.constants import PREVIEW_CSV_ROWS, API_CSV_ROWS, MODEL
import openai

from modules.logger import get_logger
logger = get_logger(__name__)

pd.set_option('display.max_columns', None)

PROMPT_BASE_TEMPLATE = """
I have {length} tables in database.
{table_samples}
"""
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
SINGLE_TABLE_SAMPLE_TEMPLATE = """
table name: {name}
{sample_data}
"""

#####################
# To bypass file processing, uncomment:
# - first three lines of _get_script_to_cleanup_csv
# - and, first line of _run_script_on_df
#####################

def _get_temp_filepath_from_filename(file_name):
    return f"/tmp/{utils.convert_to_lowercase(file_name)}.csv"

def _get_script_to_cleanup_csv(file_name, df):
    # import time
    # time.sleep(3)
    # return file_name, ""
    path = _get_temp_filepath_from_filename(file_name)
    prompt = CSV_FORMAT_PROMPT_TEMPLATE.format(path=path, sample=df.head(API_CSV_ROWS))
    utils.log_num_tokens_from_string(CSV_FORMAT_SYSTEM_PROMPT + prompt)
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role": "system", "content": CSV_FORMAT_SYSTEM_PROMPT},
                  {"role": "user", "content": prompt}],
        temperature=0)
    utils.log_num_tokens_from_string(response, "response")

    res = response["choices"][0]["message"]["content"]
    code = utils.extract_code_from_string(res)
    return file_name, code

def _run_script_on_df(file_name, df, script):
    # return df
    path = _get_temp_filepath_from_filename(file_name)
    df.to_csv(path, mode="w+")
    try:
        exec(script)
    except Exception as e:
        logger.error(f"Cannot cleanup CSV: {e}")
        return None
    else:
        formatted_df = pd.read_csv(path)
        return formatted_df

def _get_csv_cleanup_script(df_map):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit each task to the executor
        futures = [executor.submit(_get_script_to_cleanup_csv, filename, df_map[filename]) for filename in df_map]
        # Since logger uses streamlit session id, threads need streamlit context
        for t in executor._threads:
            add_script_run_ctx(t)

    # Wait for all tasks to complete and retrieve results
    return [future.result() for future in concurrent.futures.as_completed(futures)]

def _process_uploaded_paths(cnx_main, cnx_sample, uploaded_files):
    df_map = {path.name: pd.read_csv(path) for path in uploaded_files}
    script_arr = _get_csv_cleanup_script(df_map)

    prompt_table_samples = []
    table_preview = [] # Set session_state will trigger rerun. Putting it at the end of this function.
    for file_name, script in script_arr:
        # Execute cleanup script against original df
        formatted_df = _run_script_on_df(file_name, df_map[file_name], script)
        # Save clean csv to DB
        table_name = utils.convert_to_lowercase(file_name)
        formatted_df.to_sql(name=table_name, con=cnx_main, index=False, if_exists='replace')
        formatted_df.head(PREVIEW_CSV_ROWS).to_sql(name=table_name, con=cnx_sample, index=False, if_exists='replace')
        # Save clean csv to system prompt
        prompt_table_samples.append(SINGLE_TABLE_SAMPLE_TEMPLATE.format(name=table_name, sample_data=formatted_df.head(API_CSV_ROWS)))
        # Update table preview
        table_preview.append((file_name, df_map[file_name].head(PREVIEW_CSV_ROWS)))

    ### TODO: add info about unique & null item
    prompt_base = PROMPT_BASE_TEMPLATE.format(length=len(uploaded_files), table_samples="\n".join(prompt_table_samples))
    append_non_user_message("system", prompt_base)
    logger.debug(f"prompt base: {prompt_base}")
    st.session_state.table_preview = table_preview

def handle_upload(cnx_main, cnx_sample):
    """
    Handles and display uploaded_file, and save them to db.
    """
    if not st.session_state.table_preview:
        upload_form = st.empty()
        with upload_form.form("upload_form"):
            uploaded_files = st.file_uploader("upload", key=st.session_state.id, accept_multiple_files=True, type="csv",
                                              label_visibility="collapsed")
            uploaded = st.form_submit_button("Upload")
            if uploaded and len(uploaded_files) > 0:
                upload_form.empty()

        if uploaded and len(uploaded_files) > 0:
            # upload_form.empty()
            logger.info(f"received {len(uploaded_files)} uploaded files.")
            with st.spinner("Processing uploaded files. This takes approximately 30s."):
                _process_uploaded_paths(cnx_main, cnx_sample, uploaded_files)

