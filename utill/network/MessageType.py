from enum import Enum


class MessageTypeBetweenNodes(Enum):
    NewBlock = 0
    newServerDataRequest = 1
    newServerDataTransfer = 2
    getBlocks = 3
    sendBlocks = 4
    LogOff = 5
    NewConnection = 6


class MessageTypeBetweenNodeAndClient(Enum):
    LOG_IN = 0

    SIGN_UP = 1
    SIGN_UP_ANSWER = 2
    SIGN_UP_CONFIRMED = 3
    SIGN_UP_FAILED = 4
