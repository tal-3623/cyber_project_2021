from enum import Enum


class AddBlockStatus(Enum):
    INVALID_BLOCK = 1
    ORPHAN_BLOCK = 2
    SUCCESSFUL = 3
