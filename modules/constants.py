from enum import Enum

PREVIEW_CSV_ROWS = 3
API_CSV_ROWS = 2

class PendingQuery(Enum):
    CONFIRM_APPLY_SQL =1
    QUERY = 2

