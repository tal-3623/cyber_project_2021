from enum import Enum


class MessageType(Enum):
    # MessageType{
    NewBlock = 0
    newServerDataRequest = 1
    newServerDataTransfer = 2
    getBlocks = 3
    sendBlocks = 4
    LogOff = 5
    NewConnection = 6
    # }

    # MessageTypeBetweenNodeAndClient{
    # log in{
    LOG_IN_REQUEST = 7
    LOG_IN_RAND = 8
    LOG_IN_RAND_ANSWER = 9
    LOG_IN_ACCEPTED = 10
    LOG_IN_FAILED = 11
    # }

    # sign up{
    SIGN_UP = 12
    SIGN_UP_ANSWER = 13
    SIGN_UP_CONFIRMED = 14
    SIGN_UP_FAILED = 15
    # }

    # transactions{
    TRANSACTION_COMPLETED = 16
    TRANSACTION_OFFERED = 17
    GET_ALL_TRANSACTIONS = 18
    RECEIVE_ALL_TRANSACTIONS = 19
    BLOCK_UPLOADED = 20
    TRANSACTION_FAILED_DUE_TO_INVALID_NAME = 21
    TRANSACTION_FAILED_DUE_TO_MONEY =22
    # }
    # }


# class MessageType(Enum):
#     NewBlock = 0
#     newServerDataRequest = 1
#     newServerDataTransfer = 2
#     getBlocks = 3
#     sendBlocks = 4
#     LogOff = 5
#     NewConnection = 6


# class MessageType(Enum):
#     # log in{
#     LOG_IN_REQUEST = 7
#     LOG_IN_RAND = 8
#     LOG_IN_RAND_ANSWER = 9
#     LOG_IN_ACCEPTED = 10
#     LOG_IN_FAILED = 11
#     # }
#
#     # sign up{
#     SIGN_UP = 12
#     SIGN_UP_ANSWER = 13
#     SIGN_UP_CONFIRMED = 14
#     SIGN_UP_FAILED = 15
#     # }
#
#     # transactions{
#     TRANSACTION_COMPLETED = 16
#     TRANSACTION_OFFERED = 17
#     GET_ALL_TRANSACTIONS = 18
#     RECEIVE_ALL_TRANSACTIONS = 19
#     BLOCK_UPLOADED = 20
#     # }
