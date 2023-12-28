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


CSV_FORMAT_SYSTEM_PROMPT = "You help users format CSV to database."
CSV_FORMAT_PROMPT_TEMPLATE = """
I have one CSV file at path "{path}". Here are the first 3 rows: 
{sample}

Please cleanup and format the csv so that I can save it to a database. 

Return python script to read from path, format the CSV, and write back to original path.

Some cleanup examples:
1. Remove all comma in numbers. 1,234 -> 1234
2. Remove price symbols. $1,234.5 -> 1234.5
3. Convert column head to lower case and replace space with underscore. "Total NTV" -> "total_ntv"
"""

def format_csv(df):
    # Write df to tmp path
    tmp_path = f"/tmp/{utils.generate_random_string()}.csv"

    df.to_csv(tmp_path)

    print(tmp_path)

    prompt = CSV_FORMAT_PROMPT_TEMPLATE.format(path=tmp_path, sample=df.head(constants.PREVIEW_CSV_ROWS))

    with get_openai_callback() as cb:
        response = openai.ChatCompletion.create(
            model=constants.MODEL,
            messages=[{"role": "system", "content": CSV_FORMAT_SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}])
    print(cb)

    res = response["choices"][0]["message"]["content"]

    code = utils.extract_code_from_string(res)
    print(code)
    exec(code)

    return pd.read_csv(tmp_path)


def file_path_match_cached(uploaded, cached):
    if len(uploaded) != len(cached):
        return False
    for idx, path in enumerate(uploaded):
        if path != cached[idx]:
            return False
    return True

def handle_upload(cnx):
    """
    Handles and display uploaded_file, and save them to db.
    sample data (for AI prompt) is saved in st.session_state.table_samples
    """
    uploaded_files = st.sidebar.file_uploader("upload", accept_multiple_files=True, type="csv",
                                              label_visibility="collapsed")

    if uploaded_files is not None:
        # Skip if identical to previous run
        if file_path_match_cached(uploaded_files, st.session_state.cached_upload_files):
            return

        table_samples = []
        for idx, path in enumerate(uploaded_files):
            table_name = f"table{idx}"
            df = pd.read_csv(path)

            try:
                # Cleanup csv
                new_df = format_csv(df)
            except Exception as e:
                logger.error(f"Cannot cleanup CSV: {e}")
                return
            else:
                new_df.to_sql(name=table_name, con=cnx, index=False, if_exists='replace')
                table_samples.append((table_name, new_df.head(constants.PREVIEW_CSV_ROWS)))

        st.session_state.cached_upload_files = uploaded_files
        st.session_state.table_samples = table_samples
        table_sample_as_str = "\n".join([f"{name}\n{sample}" for (name, sample) in table_samples])
        st.session_state.prompt_base = constants.PROMPT_BASE_TEMPLATE.format(length=len(table_samples), table_samples=table_sample_as_str)
        ### TODO: add info about unique & null item
        logger.info(st.session_state.prompt_base)

    else:
        st.session_state["reset_chat"] = True


