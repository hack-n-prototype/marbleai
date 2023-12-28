import string
import random
import re
import io
import sys

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
