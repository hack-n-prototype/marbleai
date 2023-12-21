import os
import importlib
import sys
import streamlit as st
from modules.spreadsheet import PandasAgent
from modules.layout import Layout
from modules.utils import Utilities
import sqlite3
import openai

from modules.logger import get_logger
logger = get_logger(__name__)

SYSTEM_PROMPT = "You help users write SQL queries."
MODEL = "gpt-4"
PROMPT_SUFFIX = "Return SQL query. Query only, no explanation. Ask questions if in doubt."

# Create your connection.
cnx = sqlite3.connect(':memory:')
cur = cnx.cursor()

def reload_module(module_name):
    """For update changes
    made to modules in localhost (press r)"""

    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]


table_tool_module = reload_module('modules.spreadsheet')
layout_module = reload_module('modules.layout')
utils_module = reload_module('modules.utils')

st.set_page_config(layout="wide", page_icon="💬", page_title="Robby | Chat-Bot 🤖")

layout, utils = Layout(), Utilities()

layout.show_header("CSV")


if not os.getenv('OPENAI_API_KEY'):
    os.environ["OPENAI_API_KEY"] = st.secrets["openai_secret_key"]
openai.api_key = os.getenv('OPENAI_API_KEY')

st.session_state.setdefault("reset_chat", False)

uploaded_data_frames = utils.handle_upload()

##### process uploaded data frame #######
prompt_prefix = f"I have {len(uploaded_data_frames)} tables.\n"

for idx, df in enumerate(uploaded_data_frames):
    table_name = f"table{idx}"
    # Convert csv to table
    df.to_sql(name=table_name, con=cnx, index=False)
    # Get table column names
    cur.execute(f"SELECT * FROM {table_name} LIMIT 0")
    col_name = [description[0] for description in cur.description]
    prompt_prefix += f"'{table_name}' has columns -- {','.join(col_name)}.\n"

logger.info(prompt_prefix)

##### end process uploaded data frame ######


if uploaded_data_frames:
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    csv_agent = PandasAgent()

    with st.form(key="query"):
        query = st.text_input(
            "Ask questions",
            value="", type="default",
            placeholder="e-g : How many rows ? "
        )
        submitted_query = st.form_submit_button("Submit")
        reset_chat_button = st.form_submit_button("Reset Chat")
        if reset_chat_button:
            st.session_state["chat_history"] = []
    if submitted_query:
        prompt = prompt_prefix + f"Now user asks: {query}. {PROMPT_SUFFIX}"

        logger.info(prompt)

        # TODO: DO NOT DO THIS OVER AND OVER AGAIN.
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}])

        sql_query = response["choices"][0]["message"]["content"]
        logger.info(sql_query)

        try:
            res = str(cur.execute(sql_query).fetchall())
            logger.info(res)
        except:
            res = sql_query

        csv_agent.update_chat_history(query, res)
        csv_agent.display_chat_history()
