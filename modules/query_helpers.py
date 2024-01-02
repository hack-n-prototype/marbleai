"""
Things related to asking openai and processing user queries
"""

import openai
from modules import button_helpers
from modules import constants
import streamlit as st
from modules import ui_helpers
from modules import utils

from modules.logger import get_logger
logger = get_logger(__name__)

# TODO: make them enums

QUERY_LABEL_SQL = "sql"
QUERY_LABEL_APPLY_SQL = "apply_sql"
QUERY_LABEL_QUERY = "query"

RESULT_LABEL_SQL = "sql"
RESULT_LABEL_ASSISTANT = "assistant"
RESULT_LABEL_ACTIONS = "actions"
RESULT_LABEL_APPLY_SQL = "apply_sql"

def _get_chat_history_for_api():
    history = []
    for item in st.session_state.messages:
        openai_message = item.get_openai_message_obj()
        if openai_message:
            history.append(openai_message)
    return history

def query_openai(use_stream=False):
    """
    chat history is updated before calling this function
    """
    history = _get_chat_history_for_api()
    utils.log_num_tokens_from_string(history)
    result = openai.ChatCompletion.create(
                model=constants.MODEL,
                messages=history,
                temperature=0,
                stream=use_stream)
    if use_stream:
        with st.chat_message("assistant"):
            response = ui_helpers.update_chat_stream(result)
    else:
        response = result["choices"][0]["message"]["content"]
    utils.log_num_tokens_from_string(response, label="response")
    return response

def handle_query(label):
    if label == QUERY_LABEL_SQL:
        ui_helpers.append_non_user_message("info", "Generating SQL queries. This may take approximately 10s.").show_on_screen()
        res = query_openai(False)
        return [(RESULT_LABEL_SQL, utils.extract_code_from_string(res))]
    elif label == QUERY_LABEL_APPLY_SQL:
        return [(RESULT_LABEL_APPLY_SQL,)]
    elif label == QUERY_LABEL_QUERY:
        res = query_openai(True)
        buttons = button_helpers.determine_buttons(res)
        return [(RESULT_LABEL_ASSISTANT, res), (RESULT_LABEL_ACTIONS, buttons)]
