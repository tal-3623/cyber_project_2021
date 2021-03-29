from enum import Enum

from utill.network.MessageType import MessageTypeBetweenNodeAndClient


class Notification(Enum):
    TRANSACTION_COMPLETED = "TRANSACTION COMPLETED"
    TRANSACTION_OFFERED = "TRANSACTION OFFERED"

    @staticmethod
    def create(type: MessageTypeBetweenNodeAndClient):
        if type == MessageTypeBetweenNodeAndClient.TRANSACTION_OFFERED:
            return Notification.TRANSACTION_OFFERED
        elif type == MessageTypeBetweenNodeAndClient.TRANSACTION_COMPLETED:
            return Notification.TRANSACTION_COMPLETED
