from modules import utils
import openai
from modules import constants
import pandas as pd

from modules.logger import get_logger
logger = get_logger(__name__)

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

SINGLE_TABLE_SAMPLE_TEMPLATAE = """
table name: {name}
{sample_data}
"""

def _get_script_to_cleanup_csv(path, sample):
    prompt = CSV_FORMAT_PROMPT_TEMPLATE.format(path=path, sample=sample)
    utils.log_num_tokens_from_string(CSV_FORMAT_SYSTEM_PROMPT + prompt)
    response = openai.ChatCompletion.create(
        model=constants.MODEL,
        messages=[{"role": "system", "content": CSV_FORMAT_SYSTEM_PROMPT},
                  {"role": "user", "content": prompt}],
        temperature=0)
    utils.log_num_tokens_from_string(response, "response")

    res = response["choices"][0]["message"]["content"]
    code = utils.extract_code_from_string(res)
    return code

class TableInfo:
    def __init__(self, file_name, original_sample):
        self.table_name = utils.convert_to_lowercase(file_name)
        self.script = _get_script_to_cleanup_csv(self._get_tmp_file_path(), original_sample)
        self.original_sample = original_sample
        self.formatted_sample = None

    def __str__(self):
        return f"TableInfo(table_name={self.table_name}, script={self.script}, original_sample={self.original_sample}, formatted_sample={self.formatted_sample})"

    def format_df_and_update_formatted_sample(self, original_df):
        # self.formatted_sample = original_df.head(constants.PREVIEW_CSV_ROWS)
        # return original_df
        path = self._get_tmp_file_path()
        original_df.to_csv(path, mode="w+")
        try:
            exec(self.script)
        except Exception as e:
            logger.error(f"Cannot cleanup CSV: {e}")
            return None
        else:
            formatted_df = pd.read_csv(path)
            self.formatted_sample = formatted_df.head(constants.PREVIEW_CSV_ROWS)
            return formatted_df

    def _get_tmp_file_path(self):
        return f"/tmp/{self.table_name}"

def format_table_info_dict(dict):
    return "\n".join([SINGLE_TABLE_SAMPLE_TEMPLATAE.format(name=item.table_name, sample_data=item.formatted_sample) for item in
               dict.values()])
