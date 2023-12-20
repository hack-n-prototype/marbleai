#!/usr/bin/env python3

import pandas as pd
from langchain.llms import OpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.callbacks import get_openai_callback

FILE_PATH1 = "/Users/hazelguo/Downloads/Healthcare Price Lists - Sheet1.csv"
FILE_PATH2 = "/Users/hazelguo/Downloads/Healthcare Price Lists - Sheet2.csv"

df1 = pd.read_csv(FILE_PATH1)
df2 = pd.read_csv(FILE_PATH2)
df3 = pd.merge(df1, df2, on="Provider")

with get_openai_callback() as cb:
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df3, verbose=True)

    print(agent.run("Return the price list link for providers at location A"))

    print(cb)
