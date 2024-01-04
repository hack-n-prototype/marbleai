from enum import Enum

MODEL = "gpt-4-1106-preview"
PREVIEW_CSV_ROWS = 3
API_CSV_ROWS = 2

class PendingQuery(Enum):
    GENERATE_SQL = 1
    CONFIRM_APPLY_SQL = 2
    QUERY = 3

