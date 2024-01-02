import string
import random
import re
import tiktoken
from modules import constants

from modules.logger import get_logger
logger = get_logger(__name__)

def generate_random_string(length=30, charset=string.ascii_letters + string.digits):
    return ''.join(random.choice(charset) for _ in range(length))

def extract_code_from_string(text):
    """
    Extract code from openai response
    """
    # Regular expression to find code blocks wrapped in triple backticks
    pattern = r"```(?:\w*\n)?(.*?)```"
    # Using re.DOTALL to make '.' match any character including newline
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0]

def convert_to_lowercase(s):
    """
    Convert a string to lowercase and keep only alphanumeric characters or numbers.
    """
    # Convert the string to lowercase
    lowercase_string = s.lower()

    # Keep only alphabetic characters
    cleaned_string = ''.join(char for char in lowercase_string if char.isalnum())

    return cleaned_string

encoding = tiktoken.encoding_for_model(constants.MODEL)
def log_num_tokens_from_string(content, label="query"):
    PRICING = {
        "gpt-4-1106-preview-query": 0.01,
        "gpt-4-1106-preview-response": 0.03,
        "gpt-4-query": 0.03,
        "gpt-4-response": 0.06,
        "gpt-3.5-turbo-1106-query": 0.001,
        "gpt-3.5-turbo-1106-response": 0.002

    }
    length = len(encoding.encode(str(content)))
    logger.debug(f"[{label}] token length: " + str(length))
    entry = f"{constants.MODEL}-{label}"
    if entry in PRICING:
        logger.debug(f"[{label}] spend: $" + str(PRICING[entry] * length/1000.0))
    else:
        logger.debug(f"{entry} doesn't exist")


def format_sqlite3_cursor(cursor_data):
    """
    Formats the sqlite3.Cursor object data to a more human-readable form.

    Args:
    cursor_data (list of tuples): Data from the sqlite3.Cursor object.

    Returns:
    str: Formatted string.
    """
    formatted_output = []
    for row in cursor_data:
        # Convert each tuple to a string and join elements with a comma
        formatted_row = ", ".join(str(item) for item in row)
        formatted_output.append(formatted_row)

    # Join all rows with a newline character
    return "\n".join(formatted_output)

