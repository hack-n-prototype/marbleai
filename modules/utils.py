import pandas as pd
import streamlit as st
import string
import random
import re
import io
import sys

from modules.logger import get_logger
logger = get_logger(__name__)

PREVIEW_CSV_ROWS = 2
SINGLE_CSV_INFO = """
path{idx}: {path}
sample{idx}: 
{sample}
"""
class Utilities:

    @staticmethod
    def generate_random_string(length=30, charset=string.ascii_letters + string.digits):
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
                    st.table(df.head(PREVIEW_CSV_ROWS))
        else:
            st.session_state["reset_chat"] = True

        return data_frames

    @staticmethod
    # TODO: does it write file to /tmp/ over and over again??
    def handle_uploaded_df(uploaded_data_frames):
        """
        Write file to /tmp/
        Generate prompt db_info
        """
        df_info = f"I have {len(uploaded_data_frames)} CSV files. Here are file paths and sample data.\n"

        for idx, df in enumerate(uploaded_data_frames):
            tmp_path = f"/tmp/{Utilities.generate_random_string()}"
            df.to_csv(tmp_path)
            df_info += SINGLE_CSV_INFO.format(idx=idx, path=tmp_path, sample=df.head(PREVIEW_CSV_ROWS))


        return df_info

    @staticmethod
    def extract_code_from_string(text):
        # Regular expression to find code blocks wrapped in triple backticks
        pattern = r"```(?:\w*\n)?(.*?)```"
        # Using re.DOTALL to make '.' match any character including newline
        matches = re.findall(pattern, text, re.DOTALL)
        return matches[0]

    @staticmethod
    def capture_exec_stdout(code):
        # Create a StringIO object to capture output
        output_buffer = io.StringIO()

        # Save the current stdout
        current_stdout = sys.stdout

        # Redirect stdout to the buffer
        sys.stdout = output_buffer

        try:
            # Execute the code
            exec(code)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return None
        else:
            # Restore stdout
            sys.stdout = current_stdout

            # Get the content of the buffer
            output = output_buffer.getvalue()

            # Close the buffer
            output_buffer.close()

            return output


