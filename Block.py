import datetime
import hashlib
import json

from Transaction import Transaction
from User import User


class Block:
    def __init__(self, uploader_username: str, list_of_transactions: list, list_of_new_users: list,
                 last_block_hash: str, timestamp: str = str(datetime.datetime.now()), current_block_hash: str = None):
        """
        Constructor for the `Block` class.
        :param index: Unique ID of the block.
        :param list_of_transactions: List of transactions.
        :param timestamp: Time of generation of the block.
        :param last_block_hash: Hash of the previous block in the chain which this block is part of (hexadecimal).
        :param list_of_new_users: list of all the new users (username,pk, balance = 0)
        :param uploader_username: the user name of the block owner that uploaded it
        """
        # table related {
        self.id = None
        self.parent_id = None
        self.sequence_number = None
        self.level = None
        self.security_number = None
        # }

        # actual data related{
        self.uploader_username = uploader_username
        self.last_block_hash = last_block_hash
        self.proof_of_work = ''  # TODO
        self.timestamp = timestamp
        self.list_of_transactions = list_of_transactions
        self.list_of_new_users = list_of_new_users
        if current_block_hash is None:
            self.current_block_hash = self.compute_hash()
        else:
            self.current_block_hash = self.compute_hash()
            if self.current_block_hash != current_block_hash:  # check if real hash match
                raise Exception(
                    f'the hash does not match \n actual -> {self.current_block_hash} \n given -> {current_block_hash}')
        # }

    def set_table_parameters(self, id: int, parent_id: int, sequence_number: int, level: int, security_number: int = 0):
        self.id = id  # TODO: maybe delete
        self.parent_id = parent_id
        self.sequence_number = sequence_number
        self.level = level
        self.security_number = security_number

    @staticmethod
    def create_block_from_tuple_received(tup):
        uploader_username, timestamp, list_of_transactions_as_str, list_of_new_users_as_str, pow,last_block_hash = tup
        list_of_new_users_as_str = json.loads(list_of_new_users_as_str)
        list_of_transactions_as_str = json.loads(list_of_transactions_as_str)
        list_of_new_users = [User.create_from_str(user_as_str) for user_as_str in list_of_new_users_as_str]
        list_of_transactions = [Transaction.create_from_str(block_as_str) for block_as_str in
                                list_of_transactions_as_str]
        b = Block(uploader_username, list_of_transactions, list_of_new_users,last_block_hash,timestamp=timestamp)
        b.proof_of_work = pow
        return b


    @staticmethod
    def create_block_from_tuple(tup: tuple):
        id, parent_id, sequence_number, level, security_number, uploader_username, last_block_hash, current_block_hash, proof_of_work, timestamp, list_of_transactions, list_of_new_users = tup
        list_of_new_users_as_str = json.loads(list_of_new_users)
        list_of_transactions_as_str = json.loads(list_of_transactions)
        list_of_new_users = []
        list_of_transactions = []

        for i in list_of_new_users_as_str:
            list_of_new_users.append(User.create_from_str(i))

        for i in list_of_transactions_as_str:
            t = Transaction.create_from_str(i)
            list_of_transactions.append(t)
        b = Block(uploader_username, list_of_transactions, list_of_new_users, last_block_hash, timestamp,
                  current_block_hash)
        b.set_table_parameters(id, parent_id, sequence_number, level, security_number)
        return b

    def as_str(self) -> str:
        """
        :return: a string of the block (only data related not table NO LBH,POW)
        """
        # TODO
        list_of_new_users_as_str = []
        list_of_transactions_as_str = []

        for user in self.list_of_new_users:
            list_of_new_users_as_str.append(user.as_str())

        for tran in self.list_of_transactions:
            list_of_transactions_as_str.append(tran.as_str())

        list_of_data = [self.uploader_username, self.timestamp,
                        json.dumps(list_of_transactions_as_str), json.dumps(list_of_new_users_as_str)]
        json_string = json.dumps(list_of_data)
        return json_string

    def as_str_to_send(self) -> str:
        list_of_new_users_as_str = [user.as_str() for user in self.list_of_new_users]
        list_of_transactions_as_str = [tran.as_str() for tran in self.list_of_transactions]

        list_of_data = [self.uploader_username, self.timestamp,
                        json.dumps(list_of_transactions_as_str), json.dumps(list_of_new_users_as_str),
                        self.proof_of_work, self.last_block_hash]
        json_string = json.dumps(list_of_data)
        return json_string

    def calculate_proof_of_work(self):
        """
        self.previous hash: the  hash of the last block
        :return: the proof of work
        """
        # TODO

    def compute_hash(self) -> str:
        """
        :returns the hash of the block instance in hexadecimal
        """
        s = hashlib.sha256(self.as_str().encode()).hexdigest()
        return s
