import os
import pandas as pd
import streamlit as st

class Utilities:


    @staticmethod
    def handle_upload():
        """
        Handles and display uploaded_file
        """
        uploaded_files = st.sidebar.file_uploader("upload", accept_multiple_files=True, type="csv", label_visibility="collapsed")
        if uploaded_files is not None:
            data_frames = []
            for path in uploaded_files:
                data_frames.append(pd.read_csv(path))

            for df in data_frames:
                st.table(df)

        else:
            st.session_state["reset_chat"] = True

        return data_frames


    
