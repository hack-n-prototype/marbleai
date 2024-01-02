MODEL = "gpt-4-1106-preview"
PREVIEW_CSV_ROWS = 5
API_CSV_ROWS = 2

QUERY_PROMPT_TEMPLATE = """
User ask: {query}
Explain SQL steps to answer user query. Don't provide SQL queries. Data is clean and well-formatted. Keep answer short, ideally under 300 char.
"""




