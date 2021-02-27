import sqlite3
import threading

from Block import Block


class ServerDatabase:
    class NodesAddressTable:
        """
        the NodesAddressTable consist of a table that has two parameters
        ip|port
        """

        def __init__(self, database_cursor: sqlite3.Cursor, connection: sqlite3.Connection):
            self.connection = connection
            self.cursor = database_cursor
            self.table_name = 'NodesAddressTable'
            self.create_table()

        def create_table(self):
            self.cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {self.table_name} (IP varchar(20) UNIQUE,PORT int);''')

    class BlockchainTable:
        """
        the Blockchain table consist of a table that has 12 parameters
        UploaderUsername|ID|parentID|SequenceNumber|Level|SecurityNumber|LBH(lastBlockHash)|CBH(CurrentBlockHash)|POW(proof of work)|TimeStamp|LOT(listOfTransactions)|LONW(ListOfNewUsers)
        """

        def __init__(self, database_cursor: sqlite3.Cursor, connection: sqlite3.Connection,
                     memory_cursor: sqlite3.Cursor, memory_connection: sqlite3.Connection):
            self.connection = connection
            self.cursor = database_cursor
            self.memory_cursor = memory_cursor
            self.memory_connection = memory_connection
            self.table_name = 'Blockchain'
            self.create_table()
            self.orphans_list = []

        def calculate_security_number_threshold(self) -> int:
            # TODO
            return 5

        def create_table(self):
            self.cursor.execute(f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';''')
            result = len(self.cursor.fetchall())
            create_table_command = f'''CREATE TABLE  {self.table_name} (ID INTEGER PRIMARY KEY,ParentId INTEGER,SequenceNumber INTEGER,Level INTEGER,SecurityNumber INTEGER,UploaderUsername VARCHAR(256),LBH VARCHAR(257),CBH VARCHAR(257),POW VARCHAR(257), TimeStamp VARCHAR(255),LOT JSON,LONW JSON);'''
            if result == 0:  # aka table does not exist
                self.cursor.execute(
                    create_table_command)
                self.memory_cursor.execute(create_table_command)
            elif result == 1:  # aka table already exist
                self.memory_cursor.execute(create_table_command)
                q = f'''SELECT * FROM Blockchain WHERE SecurityNumber <{self.calculate_security_number_threshold()}'''
                self.cursor.execute(q)
                list_of_all_blocks_to_memory = self.cursor.fetchall()
                for block in list_of_all_blocks_to_memory:
                    # TODO : check if works, if not then construct the string properly
                    q = f'''INSERT INTO Blockchain VALUES {block}'''
                    self.memory_cursor.execute(q)
            else:
                raise Exception('duplicate tables')

        def add_block(self, block: Block) -> None:
            """
            :param block: the block to add to the database
            :return: None
            """
            self.cursor.execute(f'''''')
        # TODO

    class UsersTable:
        MAX_BALANCE_DIGIT_LEN = 10
        MAX_BALANCE_DIGIT_LEN_AFTER_DOT = 10
        """
        the users table consist of a table that has three parameters
        username|publicKey|balance
        """""

        def __init__(self, database_cursor: sqlite3.Cursor, connection: sqlite3.Connection):
            self.connection = connection
            self.cursor = database_cursor
            self.table_name = 'Users'
            self.create_table()

        def create_table(self):
            self.cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {self.table_name} (Username int UNIQUE,PublicKey varchar(256) UNIQUE,Balance DOUBLE({self.MAX_BALANCE_DIGIT_LEN}, {self.MAX_BALANCE_DIGIT_LEN_AFTER_DOT}));''')

        def get_balance(self, username: str) -> float:
            self.cursor.execute(f'''SELECT Balance FROM {self.table_name} WHERE Username='{username}';''')
            rows = self.cursor.fetchall()
            return rows[0][0]

        def get_public_key(self, username: str):
            self.cursor.execute(f'''SELECT PublicKey FROM {self.table_name} WHERE Username='{username}';''')
            rows = self.cursor.fetchall()
            return rows[0][0]

        def add_user(self, username: str, pk, balance: int = 0):
            s = f'''INSERT INTO {self.table_name} (Username, PublicKey, Balance) VALUES('{username}','{pk}', '{balance}');'''
            try:
                self.cursor.execute(s)
            except sqlite3.IntegrityError as e:
                print(e)
                pass

        def update_balance(self, username: str, new_balance):
            s = f'''UPDATE {self.table_name} SET Balance = {new_balance} WHERE Username = '{username}' '''
            self.cursor.execute(s)

    def __init__(self, username: str):
        """
        :param username: username of the database
        """
        self.username = username
        self.database_name = username
        self.__connection, self.__memory_connection = self.connect_to_db()
        self.__cursor, self.__memory_cursor = self.__connection.cursor(), self.__memory_connection.cursor()
        self.__lock = threading.Lock()

        self.users_table = self.UsersTable(self.__cursor, self.__connection)
        self.blockchain_table = self.BlockchainTable(self.__cursor, self.__connection, self.__memory_cursor,
                                                     self.__memory_connection)

    def connect_to_db(self):
        return sqlite3.connect(f'{self.username}.db'), sqlite3.connect(':memory:')

    def acquire(self):
        self.__lock.acquire()

    def release(self):
        self.__connection.commit()
        self.__lock.release()

    def close(self):
        self.__connection.close()
