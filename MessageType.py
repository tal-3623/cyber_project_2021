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
    pass  # TODO: add all types of messages
