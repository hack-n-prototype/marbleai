MODEL = "gpt-4-1106-preview"
PREVIEW_CSV_ROWS = 2

############
# Query
############

BUTTON_TEXT_PROCEED = "Looks good, proceed!"
BUTTON_TEXT_JOIN_DETAILS = "Tell me more about join"
QUERY_PROMPT_TEMPLATE = """
User ask: {query}
Explain SQL steps to answer user query. Don't provide SQL queries. Data is clean and well-formatted. Keep answer short, ideally under 300 char.
"""

PROCEED_PROMPT = """
Return SQL queries for initial user query. SQL only, no explanation. 
"""

JOIN_PROMPT = """
Explain different types of joins in SQL, clarify which one to use and why. Keep answer short, ideally under 300 char.
"""

BUTTON_TEXT_TO_PROMPT = {
    BUTTON_TEXT_PROCEED: PROCEED_PROMPT,
    BUTTON_TEXT_JOIN_DETAILS: JOIN_PROMPT
}



