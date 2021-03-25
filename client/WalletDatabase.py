import hashlib
import json
import sqlite3

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
            create_table_command = f'''CREATE TABLE  {self.__table_name} (Username VARCHAR(255),PasswordHash VARCHAR(256),PublicKey VARCHAR(256),PrivateKey JSON);'''
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
            print('before', private_key.as_str())
            private_key_encrypted = json.dumps([ord(char) + key_for_encryption for char in private_key.as_str()])
            command = f'''INSERT INTO Users (Username,PasswordHash,PublicKey,PrivateKey) VALUES ('{username}','{password_sha_256}','{public_key.as_str()}','{private_key_encrypted}')'''
            print('eexexexeeeeeex')
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
        # self.print_data()

    def is_user_exist(self, username: str) -> bool:
        self.__cursor.execute(f'''SELECT * FROM Users WHERE Username='{username}';''')
        rows = self.__cursor.fetchall()
        return not len(rows) == 0

    def check_if_password_valid(self, username: str, password: str):
        self.__cursor.execute(f'''SELECT * FROM Users WHERE Username='{username}';''')
        rows = self.__cursor.fetchall()
        tup = rows[0]
        username, real_password_hash, pk, sk = tup
        print(tup)
        my_password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(my_password_hash)
        print(real_password_hash)
        return my_password_hash == real_password_hash

    def get_keys(self, username: str, password: str):
        self.__cursor.execute(f'''SELECT * FROM Users WHERE Username='{username}';''')
        rows = self.__cursor.fetchall()
        tup = rows[0]
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        key_for_encryption = int(password_md5, base=16)
        username, real_password_hash, pk, sk = tup
        pk = Key.create_from_str(pk)
        sk = json.loads(sk)
        sk = ''.join([chr(num - key_for_encryption) for num in sk])
        private_key = Key.create_from_str(sk)
        return pk, private_key
