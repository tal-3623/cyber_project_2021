from enum import Enum

from utill.network.MessageType import MessageType


class Notification(Enum):
    TRANSACTION_COMPLETED = "TRANSACTION COMPLETED"
    TRANSACTION_OFFERED = "TRANSACTION OFFERED"
    TRANSACTION_FAILED_DUE_TO_MONEY = "TRANSACTION FAILED BECAUSE THE SENDING ACCOUNT DOES NOT HAVE ENOUGH MONEY"
    TRANSACTION_FAILED_DUE_TO_INVALID_NAME = "TRANSACTION FAILED BECAUSE ONE OF THE ACCOUNTS DOES NOT EXIST"

    @staticmethod
    def create(type: MessageType):
        if type == MessageType.TRANSACTION_OFFERED:
            return Notification.TRANSACTION_OFFERED
        elif type == MessageType.TRANSACTION_COMPLETED:
            return Notification.TRANSACTION_COMPLETED
        elif type == MessageType.TRANSACTION_FAILED_DUE_TO_MONEY:
            return Notification.TRANSACTION_FAILED_DUE_TO_MONEY
        elif type == MessageType.TRANSACTION_FAILED_DUE_TO_INVALID_NAME:
            return Notification.TRANSACTION_FAILED_DUE_TO_INVALID_NAME
        else:
            print('erorr')
