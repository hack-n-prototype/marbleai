"""
Things related to asking openai and processing user queries
"""

import openai
from modules import button_helpers
from modules import constants
import streamlit as st
from modules import ui_helpers
from modules import utils
from modules.constants import BUTTON_TEXT_PROCEED, BUTTON_TEXT_JOIN_DETAILS

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

def button_click_proceed():
    res = query_openai(False)
    return [("sql", utils.extract_code_from_string(res))]

def button_click_join():
    # res = query_openai(JOIN_PROMPT_TEMPLATE, True)
    # return [("assistant", res), ("actions", [button_helpers.Button.BUTTON_TEXT_PROCEED])]
    res = query_openai(True)
    return [("assistant", res), ("actions", [BUTTON_TEXT_PROCEED])]

def handle_button_click(text):
    return BUTTON_TO_FUNC[button_helpers.string_to_button(text)]()

def answer_user_query():
    res = query_openai(True)
    return res

BUTTON_TO_FUNC = {
    button_helpers.Button.BUTTON_TEXT_PROCEED: button_click_proceed,
    button_helpers.Button.BUTTON_TEXT_JOIN_DETAILS: button_click_join
}