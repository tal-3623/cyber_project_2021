from utill.GneralFunctions import GeneralFunctions


class Block:
    def __init__(self, index, list_of_transactions: list, list_of_new_users: list, timestamp, previous_hash):
        """
        Constructor for the `Block` class.
        :param index: Unique ID of the block.
        :param list_of_transactions: List of transactions.
        :param timestamp: Time of generation of the block.
        :param previous_hash: Hash of the previous block in the chain which this block is part of.
        :param list_of_new_users: list of all the new users (username,pk, balance = 0)
        """
        self.index = index
        self.list_of_transactions = list_of_transactions
        self.list_of_new_users = list_of_new_users
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.proof_of_work = None

    def calculate_hash(self):
        """

        :return: the block's hash
        """
        return GeneralFunctions.double_hash(self.encode())

    def as_bytes(self):
        return str(self).encode()

    def calculate_proof_of_work(self):
        """
        self.previous hash: the  hash of the last block
        :return: the proof of work
        """
        # TODO

    def compute_hash(self) -> str:
        """
        :returns the hash of the block instance
        """
        return GeneralFunctions.double_hash(self.as_bytes())
