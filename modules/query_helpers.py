"""
Things related to asking openai and processing user queries
"""
import openai
from modules import constants
import streamlit as st
from modules import utils
from modules.constants import PREVIEW_CSV_ROWS, STOP_TOKEN

from modules.logger import get_logger
logger = get_logger(__name__)

def _update_chat_stream(result):
    message_placeholder = st.empty()
    full_response = ""
    follow_ups = ""
    for response in result:
        if response["choices"][0].delta:
            content = response["choices"][0].delta.content or ""
            if follow_ups or STOP_TOKEN in content:
                follow_ups += content
            else:
                full_response += content
        else:
            full_response += ""
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response, utils.cleanup_array(follow_ups.split(STOP_TOKEN))

def _get_chat_history_for_api():
    history = []
    for item in st.session_state.messages:
        if openai_message:= item.get_openai_message_obj():
            history.append(openai_message)
    return history

def query_openai_w_stream():
    history = _get_chat_history_for_api()
    utils.log_num_tokens_from_string(history)
    result = openai.ChatCompletion.create(
                model=constants.MODEL,
                messages=history,
                temperature=0,
                stream=True)
    with st.chat_message("assistant"):
        response, follow_ups = _update_chat_stream(result)
    utils.log_num_tokens_from_string(response, label="response")
    return response, follow_ups or []