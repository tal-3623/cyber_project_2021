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
    # log in{
    LOG_IN_REQUEST = 0
    LOG_IN_RAND = 1
    LOG_IN_RAND_ANSWER = 2
    LOG_IN_ACCEPTED = 3
    LOG_IN_FAILED = 4
    # }

    # sign up{
    SIGN_UP = 5
    SIGN_UP_ANSWER = 6
    SIGN_UP_CONFIRMED = 7
    SIGN_UP_FAILED = 8
    # }

    # transactions{
    TRANSACTION_COMPLETED = 9
    TRANSACTION_OFFERED = 10
    GET_ALL_TRANSACTIONS = 11
    RECEIVE_ALL_TRANSACTIONS = 12
    BLOCK_UPLOADED = 13
    # }
