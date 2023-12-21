#!/usr/bin/env python3

import logging
from colorlog import ColoredFormatter

LOGFORMAT = '%(log_color)s%(asctime)s - %(funcName)s - %(filename)s - %(levelname)s - %(message)s'

def get_logger(logger_name):
    formatter = ColoredFormatter(LOGFORMAT)
    stream = logging.StreamHandler()
    stream.setLevel(logging.DEBUG)
    stream.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream)

    return logger