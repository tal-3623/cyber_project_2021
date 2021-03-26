import hashlib
import json
import sqlite3

from utill.blockchain.Transaction import Transaction
from utill.encription.EncriptionKey import Key


class WalletDatabase:
    class Users:
        def __init__(self, database_cursor: sqlite3.Cursor, connection: sqlite3.Connection):
            self.__cursor = database_cursor
            self.__connection = connection
            self.__table_name = 'Users'
            self.__create_table()

        def __create_table(self):
            self.__cursor.execute(
                f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{self.__table_name}';''')
            result = len(self.__cursor.fetchall())
            create_table_command = f'''CREATE TABLE  {self.__table_name} (Username VARCHAR(255),PasswordHash VARCHAR(256),PublicKey VARCHAR(256),PrivateKey JSON,LODT JSON);'''
            if result == 0:  # aka table does not exist
                self.__cursor.execute(create_table_command)
            elif result == 1:
                pass
            else:
                raise Exception('dup tables')

        def add_new_user(self, username: str, password: str, private_key: Key, public_key: Key):
            """
            adds a user to the wallet database
            :param username:
            :param password:
            :param private_key:
            :param public_key:
            :return: None
            """
            password_sha_256 = hashlib.sha256(password.encode()).hexdigest()
            password_md5 = hashlib.md5(password.encode()).hexdigest()
            key_for_encryption = int(password_md5, base=16)
            private_key_encrypted = json.dumps([ord(char) + key_for_encryption for char in private_key.as_str()])
            command = f'''INSERT INTO Users (Username,PasswordHash,PublicKey,PrivateKey,LODT) VALUES ('{username}','{password_sha_256}','{public_key.as_str()}','{private_key_encrypted}','{json.dumps([])}')'''
            self.__cursor.execute(command)
            self.__connection.commit()

        def get_list_of_declined_transactions(self, username: str):
            """

            :param username:
            :return: the list such that every element is tran as str
            """
            command = f'''SELECT LODT FROM Users WHERE Username='{username}';'''
            self.__cursor.execute(command)
            list_of_tups = self.__cursor.fetchall()
            tup = list_of_tups[0]
            list_of_transaction = json.loads(tup[0])
            return list_of_transaction

        def add_declined_transaction(self, username: str, transaction: Transaction):
            lodt = self.get_list_of_declined_transactions(username)
            lodt.append(transaction.as_str())
            lodt_as_str = json.dumps(lodt)
            command = f'''UPDATE Users  SET LODT = '{lodt_as_str}' WHERE Username = '{username}';'''
            self.__cursor.execute(command)
            self.__connection.commit()

    def __init__(self, database_name: str):
        self.database_name = database_name
        self.__connection = self.connect_to_db()
        self.__cursor = self.__connection.cursor()
        self.users_table = WalletDatabase.Users(self.__cursor, self.__connection)

    def connect_to_db(self):
        return sqlite3.connect(f'{self.database_name}.db', check_same_thread=False)

    def add_new_user(self, username: str, password: str, private_key: Key, public_key: Key):
        self.users_table.add_new_user(username, password, private_key, public_key)


    def is_user_exist(self, username: str) -> bool:
        self.__cursor.execute(f'''SELECT * FROM Users WHERE Username='{username}';''')
        rows = self.__cursor.fetchall()
        return not len(rows) == 0

    def check_if_password_valid(self, username: str, password: str):
        self.__cursor.execute(f'''SELECT * FROM Users WHERE Username='{username}';''')
        rows = self.__cursor.fetchall()
        tup = rows[0]
        username, real_password_hash, pk, sk, lodt = tup
        my_password_hash = hashlib.sha256(password.encode()).hexdigest()
        return my_password_hash == real_password_hash

    def get_keys(self, username: str, password: str):
        self.__cursor.execute(f'''SELECT * FROM Users WHERE Username='{username}';''')
        rows = self.__cursor.fetchall()
        tup = rows[0]
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        key_for_encryption = int(password_md5, base=16)
        username, real_password_hash, pk, sk, lodt = tup
        pk = Key.create_from_str(pk)
        sk = json.loads(sk)
        sk = ''.join([chr(num - key_for_encryption) for num in sk])
        private_key = Key.create_from_str(sk)
        return pk, private_key

    def get_list_of_declined_transactions(self, username: str):
        return self.users_table.get_list_of_declined_transactions(username)

    def add_declined_transaction(self, username: str, transaction: Transaction):
        self.users_table.add_declined_transaction(username, transaction)
