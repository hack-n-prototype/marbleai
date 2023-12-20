#!/usr/bin/env python3

from langchain.agents.agent_types import AgentType
from langchain.llms import OpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.callbacks import get_openai_callback


FILE_PATH1 = "/Users/hazelguo/Downloads/Healthcare Price Lists - Sheet1.csv"
FILE_PATH2 = "/Users/hazelguo/Downloads/Healthcare Price Lists - Sheet2.csv"


with get_openai_callback() as cb:
    csv_agent = create_csv_agent(
        OpenAI(temperature=0),
        [FILE_PATH1, FILE_PATH2],
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

    print(csv_agent.run('Join the two tables by provider. Return the price list link for providers at location A'))

    print(cb)