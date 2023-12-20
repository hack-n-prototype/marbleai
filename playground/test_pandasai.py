#!/usr/bin/env python3

# https://github.com/gventuri/pandas-ai/tree/main

import os
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

FILE_PATH1 = "/Users/hazelguo/Downloads/Healthcare Price Lists - Sheet1.csv"
FILE_PATH2 = "/Users/hazelguo/Downloads/Healthcare Price Lists - Sheet2.csv"

df1 = pd.read_csv(FILE_PATH1)
df2 = pd.read_csv(FILE_PATH2)
df3 = pd.merge(df1, df2, on="Provider")

llm = OpenAI(api_token=os.getenv('OPENAI_API_KEY'))

df = SmartDataframe(df3, config={"llm": llm})
response = df.chat('Join the two tables by provider. Return the price list link for providers at location A')

if (isinstance(response, str)):
    print(response)
else:
    print(response.to_string())


