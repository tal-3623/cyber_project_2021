from enum import Enum

from utill.network.MessageType import MessageType


class Notification(Enum):
    TRANSACTION_COMPLETED = "TRANSACTION COMPLETED"
    TRANSACTION_OFFERED = "TRANSACTION OFFERED"

    @staticmethod
    def create(type: MessageType):
        if type == MessageType.TRANSACTION_OFFERED:
            return Notification.TRANSACTION_OFFERED
        elif type == MessageType.TRANSACTION_COMPLETED:
            return Notification.TRANSACTION_COMPLETED
