import datetime
import hashlib


class Block:
    def __init__(self, index, uploader_username, list_of_transactions: list, list_of_new_users: list,
                 previous_hash, timestamp=datetime.datetime.now()):
        """
        Constructor for the `Block` class.
        :param index: Unique ID of the block.
        :param list_of_transactions: List of transactions.
        :param timestamp: Time of generation of the block.
        :param previous_hash: Hash of the previous block in the chain which this block is part of.
        :param list_of_new_users: list of all the new users (username,pk, balance = 0)
        :param uploader_username: the user name of the block owner that uploaded it
        """
        self.index = index  # TODO : maybe delete
        self.uploader_username = uploader_username
        self.list_of_transactions = list_of_transactions
        self.list_of_new_users = list_of_new_users
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.proof_of_work = None
        self.hash = None

    def hex(self) -> str:
        """
        :return: a string of the block as hexadecimal number
        """
        # TODO
        return 's'

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
        return hashlib.sha256(self.hex().encode()).hexdigest()

    def process_block(self):
        """
        this function will be called every time a block has passed the threshold to be considered secure
        then and only then the block content will be taken in to account
        :return:
        """
        # TODO
