#!/usr/bin/env python3

import sqlite3
import pandas
import openai
from langchain.callbacks import get_openai_callback
import re

MODEL = "gpt-4"

FILE_PATH = "/Users/hazelguo/Downloads/tmp.csv"

PY_SYSTEM_PROMPT = "You help users convert CSV into DB"
SQL_SYSTEM_PROMPT = "You help users write SQL queries."

def extract_code_from_string(text):
    # Regular expression to find code blocks wrapped in triple backticks
    pattern = r"```(?:\w*\n)?(.*?)```"
    # Using re.DOTALL to make '.' match any character including newline
    matches = re.findall(pattern, text, re.DOTALL)
    # Stripping leading and trailing whitespace from each match
    # stripped_matches = [match.strip() for match in matches]
    return matches[0]


def cleanup_csv(path):
    df = pandas.read_csv(path)

    prompt = f"""
I have one CSV file at path "{path}". Here are the first 3 rows: 
{df.head(3)}

I want to cleanup and format the csv so that I can save it to a database. 

Return python script to read from path, format the CSV, and write back to original path. 
    """

    with get_openai_callback() as cb:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "system", "content": PY_SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}])
    print(cb)

    res = response["choices"][0]["message"]["content"]
    print(res)

    code = extract_code_from_string(res)
    try:
        exec(code)
    except:
        print("having trouble cleaning up data.")


cleanup_csv(FILE_PATH)


# Create your connection.
cnx = sqlite3.connect(':memory:')

df1 = pandas.read_csv(FILE_PATH)
df1.to_sql(name="table1", con=cnx, index=False)

query = "total of local_ntv"

cur = cnx.cursor()

prompt = f"""
I have one table. Here are sample rows:
table1
{df1.head(3)}

Now user asks: {query}.

Return SQL query. Query only, no explanation. 
"""

print(prompt)

with get_openai_callback() as cb:
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role": "system", "content": SQL_SYSTEM_PROMPT},
                  {"role": "user", "content": prompt}])

print(cb)

sql_query = response["choices"][0]["message"]["content"]
print(sql_query)

res = cur.execute(sql_query)

result = res.fetchall()
print(type(result))
print(str(result))
