"""
Things related to asking openai and processing user queries
"""

import openai
from modules import constants
import streamlit as st
from modules.message_items.utils import append_non_user_message
from modules import utils
from modules.message_items.message_item_button import determine_buttons
from modules.constants import PendingQuery, HandleQueryOption

from modules.logger import get_logger
logger = get_logger(__name__)

def _update_chat_stream(result):
    message_placeholder = st.empty()
    full_response = ""
    for response in result:
        if response["choices"][0].delta:
            full_response += (response["choices"][0].delta.content or "")
        else:
            full_response += ""
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response

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
            response = _update_chat_stream(result)
    else:
        response = result["choices"][0]["message"]["content"]
    utils.log_num_tokens_from_string(response, label="response")
    return response

def handle_query(query):
    if query[0] == PendingQuery.GENERATE_SQL:
        append_non_user_message("info", "Generating SQL queries. This may take approximately 10s.").show_on_screen()
        res = query_openai(False)
        return [(HandleQueryOption.RUN_SQL_ON_SAMPLE, utils.extract_code_from_string(res))]
    elif query[0] == PendingQuery.CONFIRM_APPLY_SQL:
        return [(HandleQueryOption.RUN_SQL_ON_MAIN, query[1])]
    elif query[0] == PendingQuery.QUERY:
        res = query_openai(True)
        arr = [(HandleQueryOption.SHOW_ASSISTANT_MSG, res)]
        buttons = determine_buttons(res)
        for button in buttons:
            arr.append((HandleQueryOption.SHOW_BUTTON, button))
        return arr
