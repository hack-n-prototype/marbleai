#!/usr/bin/env python3

# https://github.com/gventuri/pandas-ai/tree/main

import os
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

FILE_PATH = "/Users/hazelguo/Downloads/Healthcare Price Lists - Sheet1.csv"

df = pd.read_csv(FILE_PATH)

llm = OpenAI(api_token=os.getenv('OPENAI_API_KEY'))

df = SmartDataframe(df, config={"llm": llm})
response = df.chat('Which are the 5 happiest countries?')

if (isinstance(response, str)):
    print(response)
else:
    print(response.to_string())


