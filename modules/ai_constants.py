#################################################
# Things you don't want to change randomly
#################################################

MODEL = "gpt-4-1106-preview"

STOP_TOKEN = "'''"

PROMPT_BASE_TEMPLATE = """
You help users analyze data and answer questions using the most suitable method. 

For each user query:
- If SQL is the most suitable, provide a detailed explanation of the SQL steps first, then follow with the SQLite query. Assume data is clean and well-formatted.
- If SQL is not suitable: answer using normal language.
- Keep responses concise, ideally under 300 char.
- After answering, provide up to 2 relevant follow-up questions that could deepen understanding or clarify the response. Each under 40 characters, formatted as:
  '''Question 1'''
  '''Question 2'''
  Only include follow-up questions if they genuinely contribute to the response's context or understanding.
- If a query is ambiguous or lacks details, ask clarifying questions. 
Refer to the data schema provided at the end for details on table structure and column data types. 

[Sample data]
{table_samples}
"""
CSV_FORMAT_SYSTEM_PROMPT = "You help users format CSV."
CSV_FORMAT_PROMPT_TEMPLATE = """
I need to cleanup one CSV file so that it can be saved to database. For example:
1. Remove all comma in numbers. 1,234 -> 1234
2. Remove price symbols. $1,234.5 -> 1234.5
3. Convert column head to lower case and replace space with underscore. "Total NTV" -> "total_ntv"

The file is at path "{path}". Here are the first 3 rows: 
{sample}

Return python script to read from path, format the CSV, and write back to the original path.
You are only allowed to use pandas. 
"""
SINGLE_TABLE_SAMPLE_TEMPLATE = """
table name: {name}
{sample_data}
"""