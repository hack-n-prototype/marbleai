"""
Chat view handling
"""
import streamlit as st
from streamlit_chat import message

# def update_chat_history(query=None, result=None, action=None):
#     if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1][0] == "action":
#         st.session_state.chat_history.pop()

#     if query:
#         st.session_state.chat_history.append(("user", query))
#     if result:
#         st.session_state.chat_history.append(("agent", result))
#     if action:
#         st.session_state.chat_history.append(("action", action))

def update_chat_stream(result):
    message_placeholder = st.empty()
    full_response = ""
    for response in result:
        if(response["choices"][0].delta):
            full_response += (response["choices"][0].delta.content or "")
        else:
            full_response += ""
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response

def display_buttons(buttons, idx):
    for button in buttons:
        if st.button(button, key=f"{idx}_action_{button}"):
            st.session_state.button_clicked = button
            st.rerun()

def display_chat_history():
    for idx, (sender, item) in enumerate(st.session_state.chat_history):
        if sender == "user":
            message(item, is_user=True, key=f"{idx}_user")
        elif sender == "agent":
            message(item, key=f"{idx}_agent")
        elif sender == "action":
            display_buttons(item, idx)


def update_chat_history(role, content):
    if (len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "action"):
        st.session_state.messages.pop()
    st.session_state.messages.append({"role": role, "content": content})
