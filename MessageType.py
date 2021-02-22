from enum import Enum


class MESSAGE_TYPE_BWTWEEN_NODES(Enum):
    NewBlock = 0
    newServerDataRequest = 1
    newServerDataTransfer = 2
    getBlocks = 3
    sendBlocks = 4
    LogOff = 5
