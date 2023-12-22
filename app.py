import os
import importlib
import sys
import streamlit as st
from modules.spreadsheet import SheetAgent
from modules.layout import Layout
from modules.utils import Utilities
import sqlite3
import openai

from modules.logger import get_logger
logger = get_logger(__name__)

SYSTEM_PROMPT = "You help users write SQL queries."
MODEL = "gpt-4"
PROMPT_TEMPLATE = """
{df_info}
User question: {query}
Return SQL query. Query only, no explanation. Ask questions if in doubt.
"""

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

if uploaded_data_frames:
    df_info = utils.handle_uploaded_df(cnx, cur, uploaded_data_frames)
    logger.info(db_info)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    csv_agent = SheetAgent()

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
        prompt = PROMPT_TEMPLATE.format(d_info=df_info, query=query)
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
