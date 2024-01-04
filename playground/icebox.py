
def ask_for_user_email():
    st.session_state.setdefault("user_email", None)
    if st.session_state.user_email:
        return

    st.session_state.user_email = st.text_input("Your email or name: ")
    if not st.session_state.user_email:
        st.stop()
    else:
        st.rerun()


############
# reset
############
 # if st.sidebar.button("Reset Conversation"):
 #        st.session_state.table_info = {}
 #        st.session_state.messages = []
 #        st.session_state.pending_query = None
 #        st.session_state.id = utils.generate_random_string(length=10)
 #        st.rerun()


#####################
# File dedup
#####################
def dedup_files(uploaded_name_to_path):
    """
    Assuming file content is immutable (meaning if a file content changes, its name will change),
    this function refreshes table_info:
        1. if a file is deleted, remove its entry from table_info
        2. add new files
    @return: added
    """
    to_del = []
    for name, item in st.session_state.table_info.items():
        if name not in uploaded_name_to_path:
            to_del.append(name)
    logger.debug("processing uploaded file, deleted files: " + str(to_del))
    for name in to_del:
        del st.session_state.table_info[name]

    added = []
    for name in uploaded_name_to_path:
        if name not in st.session_state.table_info:
            added.append(name)
    logger.debug(f"processing uploaded file, new files: {added}")

    return added

def generate_table_sample_for_system_prompt(dict):
    arr = []
    for item in dict.values():
        arr.append(SINGLE_TABLE_SAMPLE_TEMPLATE.format(name=item.table_name,
                                                       sample_data=item.formatted_sample.head(API_CSV_ROWS)))
    return "\n".join(arr)
