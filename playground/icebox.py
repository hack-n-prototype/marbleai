
def ask_for_user_email():
    st.session_state.setdefault("user_email", None)
    if st.session_state.user_email:
        return

    st.session_state.user_email = st.text_input("Your email or name: ")
    if not st.session_state.user_email:
        st.stop()
    else:
        st.rerun()