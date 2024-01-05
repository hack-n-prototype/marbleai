import streamlit as st
import extra_streamlit_components as stx
import time

from modules.logger import get_logger
logger = get_logger(__name__)

def _get_cookie_manager():
    return stx.CookieManager()

def ask_for_user_email():
    if not _is_valid_email(st.session_state.user_email):
        # Do this to minimize session_state change
        st.session_state.user_email = _ask_for_user_email()

def _ask_for_user_email():
    cookie_manager = _get_cookie_manager()

    if _is_valid_email(user_email:= cookie_manager.get("user_email")):
        return user_email

    if _is_valid_email(user_email:= st.text_input("Your name or email: ")):
        cookie_manager.set("user_email", user_email)
        time.sleep(1) # need this so that cookie can finish writing
        return user_email
    else:
        st.stop()

def _is_valid_email(email):
    return email and len(email) > 0