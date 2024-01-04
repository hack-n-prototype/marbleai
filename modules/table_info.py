from modules import utils
import openai
from modules.constants import PREVIEW_CSV_ROWS, MODEL, API_CSV_ROWS
import pandas as pd
from modules.logger import get_logger
logger = get_logger(__name__)

pd.set_option('display.max_columns', None)

CSV_FORMAT_SYSTEM_PROMPT = "You help users format CSV."
CSV_FORMAT_PROMPT_TEMPLATE = """
I need to cleanup one CSV file so that it can be saved to database. For example:
1. Remove all comma in numbers. 1,234 -> 1234
2. Remove price symbols. $1,234.5 -> 1234.5
3. Convert column head to lower case and replace space with underscore. "Total NTV" -> "total_ntv"

The file is at path "{path}". Here are the first 3 rows: 
{sample}

Return python script to read from path, format the CSV, and write back to the original path.
You are only allowed to use pandas. 
"""

SINGLE_TABLE_SAMPLE_TEMPLATE = """
table name: {name}
{sample_data}
"""

class TableInfo:
    def __init__(self, table_name, df):
        self.table_name = table_name
        self.original_sample = df.head(PREVIEW_CSV_ROWS)


def get_script_to_cleanup_csv(path, sample):
    prompt = CSV_FORMAT_PROMPT_TEMPLATE.format(path=path, sample=sample.head(API_CSV_ROWS))
    utils.log_num_tokens_from_string(CSV_FORMAT_SYSTEM_PROMPT + prompt)
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role": "system", "content": CSV_FORMAT_SYSTEM_PROMPT},
                  {"role": "user", "content": prompt}],
        temperature=0)
    utils.log_num_tokens_from_string(response, "response")

    res = response["choices"][0]["message"]["content"]
    code = utils.extract_code_from_string(res)
    return code


def format_df(path, df, script):
    """
    Can only call this function after init other variables, eg table_name, scripts.
    """
    # return df
    df.to_csv(path, mode="w+")
    try:
        exec(script)
    except Exception as e:
        logger.error(f"Cannot cleanup CSV: {e}")
        return None
    else:
        formatted_df = pd.read_csv(path)
        return formatted_df

def convert_filename_to_temp_filepath(file_name):
    return f"/tmp/{utils.convert_to_lowercase(file_name)}"

