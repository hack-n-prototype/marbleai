import streamlit as st
import extra_streamlit_components as stx

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

def ask_for_user_email():
    if has_valid_user_email():
        return

    cookie_manager = get_manager()
    st.session_state.user_email = cookie_manager.get("user_email")
    if has_valid_user_email():
        return

    st.session_state.user_email = st.text_input("Your email: ")
    if has_valid_user_email():
        cookie_manager.set("user_email", st.session_state.user_email)
    else:
        st.stop()

def has_valid_user_email():
    if "user_email" not in st.session_state:
        return False
    if st.session_state.user_email is None:
        return False
    if len(st.session_state.user_email) == 0:
        return False
    return True