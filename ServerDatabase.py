import sqlite3
import threading

from Block import Block


class ServerDatabase:
    class BlockchainTable:
        def __init__(self, database_name: str):
            self.database_name = database_name
            self.table_name = 'BlockchainTable'

        def add_block(self, block: Block) -> None:
            """

            :param block: the block to add to the database
            :return: None
            """
        # TODO

    class UsersTable:
        """
        the users table consist of a table that has three parametrs
        uaername|publicKey|balance
        """""

        def __init__(self, database_name: str):
            self.database_name = database_name
            self.table_name = 'UsersTable'

        def get_balance(self, username: str) -> float:
            """
            :return: the amount of money that the user have
            """
            # TODO

        def get_public_key(self, username: str):
            pass
            # TODO

    def __init__(self, username: str):
        """
        :param username: username of the database
        """
        self.username = username
        self.database_name = username
        self.lock = threading.Lock()
        self.cursor = self.connect_to_db()
        self.users_table = self.UsersTable(self.database_name)
        self.blockchain_table = self.BlockchainTable(self.database_name)

    def connect_to_db(self):
        return sqlite3.connect(f'{self.username}.db')
