import streamlit as st
from modules import query_helpers

BUTTON_TEXT_GENERATE_SQL = "Looks good! Help me generate SQL queries!"
BUTTON_TEXT_JOIN_DETAILS = "Tell me more about join"
BUTTON_TEXT_APPLY_SQL_TO_MAIN_DB = "Looks good! Apply SQL to my data set!"

GENERATE_SQL_PROMPT = """
Return SQL queries for user query. SQL only, no explanation. 
"""
JOIN_DETAULS_PROMPT = """
Explain different types of joins in SQL, clarify which one to use and why. Keep answer short, ideally under 300 char.
"""

# All buttons except for proceed
BUTTON_TEXTS = [BUTTON_TEXT_JOIN_DETAILS]

BUTTON_TEXT_TO_PROMPT = {
    BUTTON_TEXT_GENERATE_SQL: GENERATE_SQL_PROMPT,
    BUTTON_TEXT_JOIN_DETAILS: JOIN_DETAULS_PROMPT,
    BUTTON_TEXT_APPLY_SQL_TO_MAIN_DB: None
}

def determine_buttons(response):
    button_list = st.session_state.vector_db.search(response)
    button_names = [x[0].page_content for x in button_list]
    button_names.append(BUTTON_TEXT_GENERATE_SQL)
    return button_names

def get_query_label_for_button(button):
    if button == BUTTON_TEXT_GENERATE_SQL:
        return query_helpers.QUERY_LABEL_SQL
    if button == BUTTON_TEXT_APPLY_SQL_TO_MAIN_DB:
        return query_helpers.QUERY_LABEL_APPLY_SQL
    else:
        return query_helpers.QUERY_LABEL_QUERY