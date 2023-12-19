import re
import sys
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
import streamlit as st
from langchain.callbacks import get_openai_callback
from streamlit_chat import message

from pandasai.llm import OpenAI
from pandasai import SmartDataframe

class PandasAgent :

    @staticmethod
    def count_tokens_agent(agent, query):
        """
        Count the tokens used by the CSV Agent
        """
        with get_openai_callback() as cb:
            result = agent(query)
            st.write(f'Spent a total of {cb.total_tokens} tokens')

        return result
    
    def __init__(self):
        pass

    def get_agent_response(self, df, query):
        # llm = OpenAI(model="gpt-4-1106-preview")
        llm = OpenAI()
        pandaAi = SmartDataframe(df, config={"llm": llm})

        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        response = pandaAi.chat(query)
        responseAsString = response if isinstance(response, str) else response.to_string()

        fig = plt.gcf()
        if fig.get_axes():
                    # Adjust the figure size
            fig.set_size_inches(12, 6)

            # Adjust the layout tightness
            plt.tight_layout()
            buf = BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            st.image(buf, caption="Generated Plot")
        
        sys.stdout = old_stdout
        return responseAsString, captured_output

    def process_agent_thoughts(self,captured_output):
        thoughts = captured_output.getvalue()
        cleaned_thoughts = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', thoughts)
        cleaned_thoughts = re.sub(r'\[1m>', '', cleaned_thoughts)
        return cleaned_thoughts

    def display_agent_thoughts(self,cleaned_thoughts):
        with st.expander("Display the agent's thoughts"):
            st.write(cleaned_thoughts)

    def update_chat_history(self,query, result):
        st.session_state.chat_history.append(("user", query))
        st.session_state.chat_history.append(("agent", result))

    def display_chat_history(self):
        for i, (sender, message_text) in enumerate(st.session_state.chat_history):
            if sender == "user":
                message(message_text, is_user=True, key=f"{i}_user")
            else:
                message(message_text, key=f"{i}")