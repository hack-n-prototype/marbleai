from enum import Enum

MODEL = "gpt-4-1106-preview"
PREVIEW_CSV_ROWS = 3
API_CSV_ROWS = 2
STOP_TOKEN = "'''"

class PendingQuery(Enum):
    CONFIRM_APPLY_SQL =1
    QUERY = 2

