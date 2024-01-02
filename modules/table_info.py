from modules import utils
import openai
from modules.constants import PREVIEW_CSV_ROWS, MODEL, API_CSV_ROWS
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

class TableInfo:
    """
    To bypass CSV processing:
    1. in __init__: uncomment "self.script = ''", and comment out "self.script = _get_script...."
    2. in _format_df: uncomment "return df"
    """
    def __init__(self, file_name, df, cnx_main, cnx_sample):
        """
        1. Init table_name, script, original_sample
        2. Format df with script, and update formatted df
        3. Write formatted_df to db
        """

        self.table_name = utils.convert_to_lowercase(file_name)
        self.original_sample = df.head(PREVIEW_CSV_ROWS)

        # Ask openai for cleanup script. The script uses tmp_file_path
        tmp_file_path = f"/tmp/{self.table_name}"
        self.script = ""
        # self.script = _get_script_to_cleanup_csv(tmp_file_path, self.original_sample)

        # Execute cleanup script against original df
        formatted_df = self._format_df(tmp_file_path, df)
        self.formatted_sample = formatted_df.head(PREVIEW_CSV_ROWS)

        # Save clean csv to DB
        formatted_df.to_sql(name=self.table_name, con=cnx_main, index=False, if_exists='replace')
        self.formatted_sample.to_sql(name=self.table_name, con=cnx_sample, index=False, if_exists='replace')

    def __str__(self):
        return f"TableInfo(table_name={self.table_name}, script={self.script}, original_sample={self.original_sample}, formatted_sample={self.formatted_sample})"

    def _format_df(self, path, df):
        """
        Can only call this function after init other variables, eg table_name, scripts.
        """
        return df
        df.to_csv(path, mode="w+")
        try:
            exec(self.script)
        except Exception as e:
            logger.error(f"Cannot cleanup CSV: {e}")
            return None
        else:
            formatted_df = pd.read_csv(path)
            return formatted_df


def generate_table_sample_for_system_prompt(dict):
    arr = []
    for item in dict.values():
        arr.append(SINGLE_TABLE_SAMPLE_TEMPLATAE.format(name=item.table_name,
                                                        sample_data=item.formatted_sample.head(API_CSV_ROWS)))
    return "\n".join(arr)
