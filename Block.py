import hashlib


class Block:
    def __init__(self, index, list_of_transactions: list, timestamp,previous_hash):
        """
        Constructor for the `Block` class.
        :param index: Unique ID of the block.
        :param list_of_transactions: List of transactions.
        :param timestamp: Time of generation of the block.
         :param previous_hash: Hash of the previous block in the chain which this block is part of.
        """
        self.index = index
        self.list_of_transactions = list_of_transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash

    def __str__(self):
        pass

    def compute_hash(self) -> str:
        """
        :returns the hash of the block instance
        """
        return hashlib.sha256(str(self)).hexdigest()
