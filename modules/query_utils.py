"""
Things related to asking openai and processing user queries
"""

import openai
from modules import constants
import streamlit as st
from modules import chat_utils
from modules import utils

from modules.logger import get_logger
logger = get_logger(__name__)

QUERY_PROMPT_TEMPLATE = """
User ask: {query}
Return the steps to answer user query with SQL. No need to cleanup or process data. No need to provide SQL queries. Keep answer concise.
"""

PROCEED_PROMPT_TEMPLATE = """
User ask: {query}
Return SQL queries. SQL only, no explanation. 
"""

JOIN_PROMPT_TEMPLATE = """
User ask: {query}
Looks like there are four different types of joins. Explain them, clarify which one you choose and why. Keep answers concise.
"""

BUTTON_TEXT_PROCEED = "Looks good, proceed!"
BUTTON_TEXT_JOIN_DETAILS = "Tell me more about join"

def query_openai(query_template):
    logger.debug("system prompt: " + st.session_state.prompt_base)
    logger.debug("user prompt: " + query_template)
    prompt = query_template.format(query=st.session_state.user_query)
    utils.log_num_tokens_from_string(st.session_state.prompt_base + prompt)
    res = openai.ChatCompletion.create(
        model=constants.MODEL,
        messages=[{"role": "system", "content": st.session_state.prompt_base},
                  {"role": "user", "content": prompt}],
        temperature=0)
    utils.log_num_tokens_from_string(res, type="response")
    return res["choices"][0]["message"]["content"]

def button_click_proceed():
    chat_utils.update_chat_history(query=BUTTON_TEXT_PROCEED)
    res = query_openai(PROCEED_PROMPT_TEMPLATE)
    return utils.extract_code_from_string(res)

def button_click_join():
    res = query_openai(JOIN_PROMPT_TEMPLATE)
    chat_utils.update_chat_history(query=BUTTON_TEXT_JOIN_DETAILS, result=res, action=[BUTTON_TEXT_PROCEED])
    return None

def handle_button_click(text):
    return BUTTON_TO_FUNC[text]()

def answer_user_query():
    res = query_openai(QUERY_PROMPT_TEMPLATE)
    chat_utils.update_chat_history(st.session_state.user_query, res, action=[BUTTON_TEXT_PROCEED, BUTTON_TEXT_JOIN_DETAILS])

BUTTON_TO_FUNC = {
    BUTTON_TEXT_PROCEED: button_click_proceed,
    BUTTON_TEXT_JOIN_DETAILS: button_click_join
}