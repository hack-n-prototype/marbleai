#!/usr/bin/env python3
import streamlit as st
import logging
from colorlog import ColoredFormatter

LOGFORMAT = '%(log_color)s%(asctime)s (%(user)s) - [%(filename)s:%(lineno)d] - %(funcName)s - %(levelname)s - %(message)s'

class CustomFormatter(ColoredFormatter):
    def format(self, record):
        record.user = st.session_state.user_email
        return super(CustomFormatter, self).format(record)

def get_logger(logger_name):
    formatter = CustomFormatter(LOGFORMAT)
    stream = logging.StreamHandler()
    stream.setLevel(logging.DEBUG)
    stream.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream)

    return logger