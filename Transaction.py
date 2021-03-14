import datetime
import json


class Transaction:

    def __init__(self, sender_username: str, receiver_username: str, amount: float, description: str,
                 timestamp: str = None, sender_signature: str = '',
                 receiver_signature: str = ''):
        # data related{
        self.sender_username = sender_username
        self.receiver_username = receiver_username
        self.amount = amount
        self.description = description
        self.timestamp = timestamp if timestamp is not None else str(datetime.datetime.now())
        # }

        # security related{
        self.sender_signature = sender_signature
        self.receiver_signature = receiver_signature
        # }

    def as_str(self):
        list_of_components = [self.sender_username, self.receiver_username, self.amount, self.description,
                              self.timestamp, self.sender_signature, self.receiver_signature]
        return json.dumps(list_of_components)

    def data_as_str(self):
        """
        no signatures
        :return:
        """
        list_of_components = [self.sender_username, self.receiver_username, self.amount, self.description,
                              self.timestamp]
        return json.dumps(list_of_components)

    @staticmethod
    def create_from_str(string: str):
        sender_username, receiver_username, amount, description, timestamp, sender_signature, receiver_signature = json.loads(
            string)
        return Transaction(sender_username, receiver_username, amount, description, timestamp, sender_signature,
                           receiver_signature)

    def to_string(self):
        print(
            f'{self.sender_username, self.receiver_username, self.amount, self.description, self.timestamp, self.sender_signature, self.receiver_signature}')

    # TODO: maybe delete
    # def verify(self, sender_pk: Key, receiver_pk: Key):
    #     if sender_pk.verify(self.receiver_signature, self.data_as_str()) and receiver_pk.verify(self.sender_signature,                                                                                    self.data_as_str()):
    #         return True
    #     else:
    #         print('')
    #         return False
