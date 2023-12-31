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
    if label == "sql":
        res = query_openai(False)
        return [("sql", utils.extract_code_from_string(res))]
    elif label == "query":
        res = query_openai(True)
        buttons = button_helpers.determine_buttons(res)
        return [("assistant", res), ("actions", buttons)]
