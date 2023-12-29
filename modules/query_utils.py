"""
Things related to asking openai and processing user queries
"""

import openai
from modules import constants
import streamlit as st
from langchain.callbacks import get_openai_callback
from modules import chat_utils

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

def query_openai(query_template, useStream=False):
    logger.debug("system prompt: " + st.session_state.prompt_base)
    logger.debug("user prompt: " + query_template)
    with get_openai_callback() as cb:
        if(useStream):
            full_response = chat_utils.update_chat_stream(openai.ChatCompletion.create(
                model=constants.MODEL,
                messages=[{"role": "system", "content": st.session_state.prompt_base},
                    {"role": "user", "content": query_template.format(query=st.session_state.user_query)}],
                temperature=0,
                max_tokens=50,
                stream=useStream,))

        else:
            full_response = openai.ChatCompletion.create(
                model=constants.MODEL,
                messages=[{"role": "system", "content": st.session_state.prompt_base},
                    {"role": "user", "content": query_template.format(query=st.session_state.user_query)}],
                max_tokens=50,
                temperature=0,
                stream=useStream)
        # st.session_state.messages.append({"role": "assistant", "content": full_response})
        # print(cb)
        # chat_utils.update_chat_history(result=full_response)
        return full_response

def button_click_proceed():
    return ("sql", query_openai(PROCEED_PROMPT_TEMPLATE, False))

def button_click_join():
    res = query_openai(JOIN_PROMPT_TEMPLATE, True)
    
    # chat_utils.update_chat_history(query=BUTTON_TEXT_JOIN_DETAILS, result=res, action=[BUTTON_TEXT_PROCEED])
    return ("text", res)

def handle_button_click(text):
    chat_utils.update_chat_history("user", text)
    st.rerun()
    return BUTTON_TO_FUNC[text]()

def answer_user_query():
    res = query_openai(QUERY_PROMPT_TEMPLATE, True)
    return res
    # chat_utils.update_chat_history(st.session_state.user_query, res, action=[BUTTON_TEXT_PROCEED, BUTTON_TEXT_JOIN_DETAILS])

BUTTON_TO_FUNC = {
    BUTTON_TEXT_PROCEED: button_click_proceed,
    BUTTON_TEXT_JOIN_DETAILS: button_click_join
}