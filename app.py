import os
import importlib
import sys
import streamlit as st
from modules.spreadsheet import SheetAgent
from modules.layout import Layout
from modules.utils import Utilities
import openai

from modules.logger import get_logger
logger = get_logger(__name__)

SYSTEM_PROMPT = "You write python script to answer user query."
MODEL = "gpt-4"
PROMPT_TEMPLATE = """
{csv_info}

User query: {query}.

Return python script to read paths and answer user's query. Ask questions if in doubt.
"""

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
    csv_info = utils.handle_uploaded_df(uploaded_data_frames)
    logger.info(csv_info)

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
        prompt = PROMPT_TEMPLATE.format(csv_info=csv_info, query=query)
        logger.info(prompt)

        # TODO: DO NOT DO THIS OVER AND OVER AGAIN.
        gpt_response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}],
            temperature=0)

        gpt_response = gpt_response["choices"][0]["message"]["content"]
        logger.info(gpt_response)
        code_exec_output = None
        try:
            code = utils.extract_code_from_string(gpt_response)
            logger.info(code)
            code_exec_output = utils.capture_exec_stdout(code)
            logger.info(code_exec_output)
        except:
            pass

        csv_agent.update_chat_history(query, code_exec_output if code_exec_output else gpt_response)
        csv_agent.display_chat_history()
