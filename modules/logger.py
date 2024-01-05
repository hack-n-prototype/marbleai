#!/usr/bin/env python3
import streamlit as st
from colorlog import ColoredFormatter

LOGFORMAT = '%(log_color)s%(asctime)s (%(user)s) - [%(filename)s:%(lineno)d] - %(funcName)s - %(levelname)s - %(message)s'

class CustomFormatter(ColoredFormatter):
    def format(self, record):
        record.user = st.session_state.user_email
        return super(CustomFormatter, self).format(record)

def get_logger(logger_name):
    logger = st.logger.get_logger(logger_name)
    logger.setLevel("DEBUG")
    # Get the Streamlit log handler
    log_handler = logger.handlers[0]
    # Set the formatter for the handler
    log_handler.setFormatter(CustomFormatter(LOGFORMAT))

    return logger
