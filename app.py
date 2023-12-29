import os
import importlib
import sys
import streamlit as st
from modules import utils
from modules import file_utils
from modules import query_utils
from modules import chat_utils
from modules import constants
import openai
import sqlite3

from modules.logger import get_logger
logger = get_logger(__name__)

def reload_module(module_name):
    """For update changes
    made to modules in localhost (press r)"""

    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]


def setup_session():
    def _set_value_if_not_exist(key, func):
        if key not in st.session_state:
            st.session_state[key] = func()

    _set_value_if_not_exist("id", lambda: utils.generate_random_string(length=10))
    _set_value_if_not_exist("chat_history", lambda: [])
    _set_value_if_not_exist("table_info", lambda: {})
    _set_value_if_not_exist("prompt_base", lambda: None)
    _set_value_if_not_exist("user_query", lambda: None)
    _set_value_if_not_exist("button_clicked", lambda: None)
    _set_value_if_not_exist("messages", lambda: [])

    st.set_page_config(layout="wide", page_icon="💬", page_title="Marble | Chat-Bot 🤖")
    st.markdown(
        "<h1 style='text-align: center;'> Ask Marble about your CSV files ! 😁</h1>",
        unsafe_allow_html=True,
    )
    st.session_state.setdefault("reset_chat", False)

    # Init openai key
    if not os.getenv('OPENAI_API_KEY'):
        os.environ["OPENAI_API_KEY"] = st.secrets["openai_secret_key"]
    openai.api_key = os.getenv('OPENAI_API_KEY')


setup_session()

cnx = sqlite3.connect(f"/tmp/{st.session_state.id}.db")
file_utils.handle_upload(cnx)


def show_item_on_screen(role, content=None):
    if (role == "action"):
        if st.button("hello"):
            st.session_state.button_clicked = query_utils.BUTTON_TEXT_JOIN_DETAILS
            # st.session_state.messages.append({"role": "user", "content": query_utils.BUTTON_TEXT_PROCEED})
            print("button clicked: ", st.session_state.button_clicked)
            st.rerun()
    else:
        with st.chat_message(role):
            st.markdown(content)

if st.session_state.table_info:
    # Show table preview
    for name, item in st.session_state.table_info.items():
        with st.expander(f"{name} sample"):
            st.dataframe(item.original_sample)


    for message in st.session_state.messages:
        show_item_on_screen(message["role"], message["content"] if "content" in message else None)
    
    # if st.button(query_utils.BUTTON_TEXT_PROCEED):
    #     st.session_state.button_clicked = query_utils.BUTTON_TEXT_PROCEED
    # logger.debug(f'clicked {st.session_state.button_clicked}')
    # logger.debug("BEFORE BUtton")
    # if st.session_state.button_clicked:
    #     sql = query_utils.handle_button_click(st.session_state.button_clicked)
    #     st.session_state.button_clicked = None
    #     logger.debug("sql: " + str(sql))
    #     if sql:
    #         res = str(cnx.cursor().execute(sql).fetchall())
    #         st.session_state.messages.append({"role": "assistant", "content": res})
    # logger.debug("AFTER SQL")
    
    if prompt := st.chat_input("e-g : How many rows ? "):
        chat_utils.update_chat_history("user", prompt)
        show_item_on_screen("user", prompt)
       

        with st.chat_message("assistant"):
            full_response = query_utils.answer_user_query()
            show_item_on_screen("action", None)
            chat_utils.update_chat_history("assistant", full_response)
            chat_utils.update_chat_history("action", query_utils.BUTTON_TEXT_JOIN_DETAILS) # TODO: update
            

    if st.session_state.button_clicked:
        st.session_state.button_clicked = None
        type, content = query_utils.handle_button_click(st.session_state.button_clicked)
        if type == "sql":
            res = str(cnx.cursor().execute(content).fetchall())
            chat_utils.update_chat_history("assistant", res)
            show_item_on_screen("assistant", res)
        else:
            chat_utils.update_chat_history("assistant", content)
        

        
        # with st.chat_message("action"):

        #     if st.button(query_utils.BUTTON_TEXT_PROCEED):
        #         st.session_state.button_clicked = query_utils.BUTTON_TEXT_PROCEED
        #         logger.debug(f'clicked {st.session_state.button_clicked}')
        #         logger.debug("outside button clicked")

            # st.session_state.messages.append({"role": "action", "content": full_response})

            # full_response = chat_utils.update_chat_stream(openai.ChatCompletion.create(
            #     model=constants.MODEL,
            #     messages=[
            #         {"role": m["role"], "content": m["content"]}
            #         for m in st.session_state.messages
            #     ],
            #     stream=True,
            # ))
            # message_placeholder = st.empty()
            # full_response = ""
            # for response in openai.ChatCompletion.create(
            #     model=constants.MODEL,
            #     messages=[
            #         {"role": m["role"], "content": m["content"]}
            #         for m in st.session_state.messages
            #     ],
            #     stream=True,
            # ):
            #     if(response.choices[0].delta):
            #         full_response += response.choices[0].delta.content
            #         message_placeholder.markdown(full_response + "▌")
            #     else:
            #         full_response += ""
            # message_placeholder.markdown(full_response)
        

    # # Show user input box
    # with st.form(key="query"):
    #     query = st.text_input(
    #         "Ask questions",
    #         value="", type="default",
    #         placeholder="e-g : How many rows ? "
    #     )
    #     submitted_query = st.form_submit_button("Submit")
    #     reset_chat_button = st.form_submit_button("Reset Chat")
    #     if reset_chat_button:
    #         st.session_state["chat_history"] = []

    # # If user submit a query
    # if submitted_query:
    #     st.session_state.user_query = query
    #     query_utils.answer_user_query()

    # # Handle button click
    # # TODO: couldn't figure out sqlite & threads. Doing it here works.
    # logger.debug("button_clicked: " +  str(st.session_state.button_clicked))
    # if st.session_state.button_clicked:
    #     sql = query_utils.handle_button_click(st.session_state.button_clicked)
    #     st.session_state.button_clicked = None
    #     logger.debug("sql: " + str(sql))
    #     if sql:
    #         res = str(cnx.cursor().execute(sql).fetchall())
    #         chat_utils.update_chat_history(result=res)

    # chat_utils.display_chat_history()
   
