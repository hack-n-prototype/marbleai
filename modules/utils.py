import pandas as pd
import streamlit as st
import string
import random

from modules.logger import get_logger
logger = get_logger(__name__)

class Utilities:

    @staticmethod
    def generate_random_string(length=10, charset=string.ascii_letters + string.digits):
        return ''.join(random.choice(charset) for _ in range(length))

    @staticmethod
    def handle_upload():
        """
        Handles and display uploaded_file
        """
        uploaded_files = st.sidebar.file_uploader("upload", accept_multiple_files=True, type="csv", label_visibility="collapsed")
        data_frames = []

        if uploaded_files is not None:
            for path in uploaded_files:
                data_frames.append(pd.read_csv(path))
            for df in data_frames:
                with st.expander("Sample table"):
                    st.table(df.head(3))
        else:
            st.session_state["reset_chat"] = True

        return data_frames

    @staticmethod
    # TODO: does it write file to /tmp/ over and over again??
    def handle_uploaded_df(connection, cursor, uploaded_data_frames):
        """
        Write file to /tmp/
        Generate prompt db_info
        """
        df_info = f"I have {len(uploaded_data_frames)} tables.\n"

        for idx, df in enumerate(uploaded_data_frames):
            table_name = f"table{idx}"
            # Convert csv to table
            df.to_sql(name=table_name, con=connection, index=False)
            # Get table column names
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
            col_name = [description[0] for description in cursor.description]
            df_info += f"'{table_name}' has columns -- {','.join(col_name)}.\n"

            # Write file to /tmp
            tmp_path = f"/tmp/{Utilities.generate_random_string()}"
            df.to_csv(tmp_path)

            # Read from /tmp
            with open(tmp_path, 'r') as file:
                content = file.read()
                logger.info(tmp_path)
                logger.info(content)

        return df_info

    
