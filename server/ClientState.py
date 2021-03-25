from enum import Enum


class ClientState(Enum):
    LOGGED_IN = 0
    NOT_LOGGED_IN = 1
    WAITING_FOR_CONFIRMATION = 2
