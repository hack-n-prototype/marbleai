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

QUERY_PROMPT_TEMPLATE = """
User ask: {query}
Explain SQL steps to answer user query. Don't provide SQL queries. Data is clean and well-formatted. Keep answer short, ideally under 300 char.
"""

PROCEED_PROMPT_TEMPLATE = """
User ask: {query}
Return SQL queries. SQL only, no explanation. 
"""

JOIN_PROMPT_TEMPLATE = """
User ask: {query}
Explain different types of joins in SQL, clarify which one to use and why. Keep answer short, ideally under 300 char.
"""

def query_openai(query_template, use_stream=False):
    prompt = query_template.format(query=st.session_state.user_query)
    logger.debug("user prompt: " + prompt)
    utils.log_num_tokens_from_string(st.session_state.prompt_base + prompt)
    result = openai.ChatCompletion.create(
                model=constants.MODEL,
                messages=[{"role": "system", "content": st.session_state.prompt_base},
                          {"role": "user", "content": prompt}],
                temperature=0,
                stream=use_stream)
    if use_stream:
        with st.chat_message("assistant"):
            response = ui_helpers.update_chat_stream(result)
    else:
        response = result["choices"][0]["message"]["content"]
    utils.log_num_tokens_from_string(response, type="response")
    return response

def button_click_proceed():
    res = query_openai(PROCEED_PROMPT_TEMPLATE, False)
    return [("sql", utils.extract_code_from_string(res))]

def button_click_join():
    res = query_openai(JOIN_PROMPT_TEMPLATE, True)
    return [("assistant", res), ("actions", [button_helpers.Button.BUTTON_TEXT_PROCEED])]

def handle_button_click(text):
    return BUTTON_TO_FUNC[button_helpers.string_to_button(text)]()

def answer_user_query():
    res = query_openai(QUERY_PROMPT_TEMPLATE, True)
    return res

BUTTON_TO_FUNC = {
    button_helpers.Button.BUTTON_TEXT_PROCEED: button_click_proceed,
    button_helpers.Button.BUTTON_TEXT_JOIN_DETAILS: button_click_join
}