"""
Things related to asking openai and processing user queries
"""
import openai
from modules import constants
import streamlit as st
from modules import utils
from modules.constants import PREVIEW_CSV_ROWS

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
        if openai_message:= item.get_openai_message_obj():
            history.append(openai_message)
    return history

def query_openai(use_stream = False):
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

def query_sql_w_status():
    status = ["Generating SQL queries. This may take approximately 10s."]
    st.write(status[-1])
    sql = utils.extract_code_from_string(query_openai(False))
    status.append(f"Applying `{sql}` on sample data (first {PREVIEW_CSV_ROWS} rows)...")
    st.write(status[-1])
    return status, sql