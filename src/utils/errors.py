from enum import Enum

class Error(Enum):
    DATETIME        = 1
    TIMEZONE        = 2
    DATE_HAS_PASSED = 3
    CHANNEL         = 4