import string
import random
import re

from modules.logger import get_logger
logger = get_logger(__name__)


def generate_random_string(length=30, charset=string.ascii_letters + string.digits):
    return ''.join(random.choice(charset) for _ in range(length))


def extract_code_from_string(text):
    # Regular expression to find code blocks wrapped in triple backticks
    pattern = r"```(?:\w*\n)?(.*?)```"
    # Using re.DOTALL to make '.' match any character including newline
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0]


def convert_to_lowercase(s):
    """
    Convert a string to lowercase and remove non-alphabetic characters.

    Parameters:
    s (str): The string to be converted.

    Returns:
    str: The converted string.
    """
    # Convert the string to lowercase
    lowercase_string = s.lower()

    # Keep only alphabetic characters
    cleaned_string = ''.join(char for char in lowercase_string if char.isalnum())

    return cleaned_string