#!/usr/bin/env python3

import pandas
import string
import random
import openai
from langchain.callbacks import get_openai_callback
import io
import sys

FILE_PATH = "/Users/hazelguo/Downloads/CSV Dummy Data Sebas - Sheet1.csv"

MODEL = "gpt-4"
SYSTEM_PROMPT = "You write python script for user query."
PROMPT_TEMPLATE = """
I have {length} CSV files. Here are file paths and sample data.
{csv_info}

User query: {query}.

Return python script to read files and answer user's query. Ask questions if in doubt.
"""

def generate_random_string(length=10, charset=string.ascii_letters + string.digits):
    return ''.join(random.choice(charset) for _ in range(length))

import re

def extract_code_from_string(text):
    # Regular expression to find code blocks wrapped in triple backticks
    pattern = r"```(?:\w*\n)?(.*?)```"
    # Using re.DOTALL to make '.' match any character including newline
    matches = re.findall(pattern, text, re.DOTALL)
    # Stripping leading and trailing whitespace from each match
    # stripped_matches = [match.strip() for match in matches]
    return matches[0]

def capture_exec_stdout(code):
    # Create a StringIO object to capture output
    output_buffer = io.StringIO()

    # Save the current stdout
    current_stdout = sys.stdout

    # Redirect stdout to the buffer
    sys.stdout = output_buffer

    try:
        # Execute the code
        exec(code)
    except:
        return None
    else:
        # Restore stdout
        sys.stdout = current_stdout

        # Get the content of the buffer
        output = output_buffer.getvalue()

        # Close the buffer
        output_buffer.close()

        return output



df = pandas.read_csv(FILE_PATH)
tmp_path = f"/tmp/{generate_random_string()}"
df.to_csv(tmp_path)

csv_info = f"""
path0: {FILE_PATH}
sample0:
{df.head(3)}
"""
prompt = PROMPT_TEMPLATE.format(length=1, csv_info=csv_info, query="sum of local_ntv")
print(prompt)
#
# with get_openai_callback() as cb:
#     response = openai.ChatCompletion.create(
#         model=MODEL,
#         messages=[{"role": "system", "content": SYSTEM_PROMPT},
#                   {"role": "user", "content": prompt}])

# print(cb)

# res = response["choices"][0]["message"]["content"]
# code = extract_code_from_string(res)
# print("#####")
# print(res)
# print("############")
#
# print(code)

code = """
import pandas as pd

# Define the file path
file_path = "/Users/hazelguo/Downloads/CSV Dummy Data Sebas - Sheet1.csv"

# Load the csv file
df = pd.read_csv(file_path)

# Convert 'local_ntv' into numerical data by removing '$' and ',' symbols and converting the string representation into float
df['local_ntv'] = df['local_ntv'].replace({'\$': '', ',': ''}, regex=True).astype(float)

# Calculate the sum of 'local_ntv'
total_local_ntv = df['local_ntv'].sum()

# Print the result
print(f"The sum of 'local_ntv' is: {total_local_ntv}")

"""
print("$$$")
output = capture_exec_stdout(code)
print(output)
