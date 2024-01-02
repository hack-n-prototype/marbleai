from enum import Enum

MODEL = "gpt-4-1106-preview"
PREVIEW_CSV_ROWS = 5
API_CSV_ROWS = 2

class PendingQuery(Enum):
    GENERATE_SQL = 1
    CONFIRM_APPLY_SQL = 2
    QUERY = 3

class HandleQueryOption(Enum):
    RUN_SQL_ON_SAMPLE = 1
    RUN_SQL_ON_MAIN = 2
    SHOW_ASSISTANT_MSG = 3
    SHOW_BUTTON = 4




