import streamlit as st

BUTTON_TEXT_PROCEED = "Looks good, proceed!"
BUTTON_TEXT_JOIN_DETAILS = "Tell me more about join"

PROCEED_PROMPT = """
Return SQL queries for initial user query. SQL only, no explanation. 
"""
JOIN_PROMPT = """
Explain different types of joins in SQL, clarify which one to use and why. Keep answer short, ideally under 300 char.
"""

# All buttons except for proceed
BUTTON_TEXTS = [BUTTON_TEXT_JOIN_DETAILS]

BUTTON_TEXT_TO_PROMPT = {
    BUTTON_TEXT_PROCEED: PROCEED_PROMPT,
    BUTTON_TEXT_JOIN_DETAILS: JOIN_PROMPT
}

def determine_buttons(response):
    button_list = st.session_state.vector_db.search(response)
    button_names = [x[0].page_content for x in button_list]
    button_names.append(BUTTON_TEXT_PROCEED)
    return button_names

def get_button_label(button):
    if button == BUTTON_TEXT_PROCEED:
        return "sql"
    else:
        return "query"