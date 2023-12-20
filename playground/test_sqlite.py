#!/usr/bin/env python3

import sqlite3
import pandas
import openai
from langchain.callbacks import get_openai_callback

FILE_PATH1 = "/Users/hazelguo/Downloads/Healthcare Price Lists - Sheet1.csv"
FILE_PATH2 = "/Users/hazelguo/Downloads/Healthcare Price Lists - Sheet2.csv"
SYSTEM_PROMPT = "You help users write SQL queries."

def get_col_names(cur, table_name):
    cur.execute(f"SELECT * FROM {table_name} LIMIT 0")
    column_names = [description[0] for description in cur.description]
    return column_names


# Create your connection.
cnx = sqlite3.connect(':memory:')

df1 = pandas.read_csv(FILE_PATH1)
df1.to_sql(name="table1", con=cnx, index=False)

df2 = pandas.read_csv(FILE_PATH2)
df2.to_sql(name="table2", con=cnx, index=False)

# execute SQL
cur = cnx.cursor()

# Execute a query

col_name1 = get_col_names(cur, "table1")
col_name2 = get_col_names(cur, "table2")
query = "Return the price list link for providers at location A"


prompt = f"""
I have two tables. 
'table1' has columns -- {','.join(col_name1)}. 
'table2' has columns -- {','.join(col_name2)}. 

Now user asks: {query}.

Return SQL query. Query only, no explanation. 
"""

print(prompt)

with get_openai_callback() as cb:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": prompt}])

sql_query = response["choices"][0]["message"]["content"]
print(sql_query)
res = cur.execute(sql_query)
print(res.fetchall())

print(cb)