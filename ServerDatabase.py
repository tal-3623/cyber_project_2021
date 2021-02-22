import sqlite3
import threading

from Block import Block


class ServerDatabase:
    __instance__ = None

    def __init__(self, username: str):
        """
        :param username: username of the database
        """
        self.username = username
        self.lock = threading.Lock()
        self.cursor = self.connect_to_db()

    def connect_to_db(self):
        return sqlite3.connect(f'{self.username}.db')

    def add_block(self, block: Block) -> None:
        """

        :param block: the block to add to the database
        :return: None
        """
    # TODO




