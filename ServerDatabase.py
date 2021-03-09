import hashlib
import json
import sqlite3
import threading

from AddBlockStatus import AddBlockStatus
from Block import Block
from Transaction import Transaction
from User import User


class ServerDatabase:
    class GeneralVariablesTable:
        def __init__(self, database_cursor: sqlite3.Cursor, connection: sqlite3.Connection):
            self.__cursor = database_cursor
            self.__connection = connection
            self.__table_name = 'GeneralVariables'
            self.__last_level_processed = None
            self.__create_table()

        def __create_table(self):
            self.__cursor.execute(
                f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{self.__table_name}';''')
            result = len(self.__cursor.fetchall())

            if result == 0:  # aka table does not exist
                create_table_command = f'''CREATE TABLE  {self.__table_name} (LLP INTEGER);'''
                self.__cursor.execute(create_table_command)
                command = f'''INSERT INTO {self.__table_name} VALUES (0)'''
                self.__cursor.execute(command)
                self.__last_level_processed = 0  # default
            elif result == 1:
                self.__cursor.execute(f'''SELECT LLP FROM {self.__table_name}''')
                rows = self.__cursor.fetchall()
                if len(rows) == 0:
                    command = f'''INSERT INTO {self.__table_name} VALUES (0)'''
                    self.__cursor.execute(command)
                    self.__last_level_processed = 0  # default
                elif len(rows) != 1:
                    raise Exception('more then one row')
                else:
                    self.__last_level_processed = rows[0][0]
            else:
                raise Exception('dup tables')

        def get_last_level_processed(self) -> int:
            return self.__last_level_processed

        def set_last_level_processed(self, level: int):
            self.__last_level_processed = level

            command = f'''UPDATE {self.__table_name} SET LLP = {level}'''
            self.__cursor.execute(command)

    class BlockchainTable:
        """
        the Blockchain table consist of a table that has 12 parameters
        ID|parentID|SequenceNumber|Level|SecurityNumber|UploaderUsername|LBH(lastBlockHash)|CBH(CurrentBlockHash)|POW(proof of work)|TimeStamp|LOT(listOfTransactions)|LONW(ListOfNewUsers)
        """

        def __init__(self, database_cursor: sqlite3.Cursor, connection: sqlite3.Connection,
                     memory_cursor: sqlite3.Cursor, memory_connection: sqlite3.Connection, general_val_table,
                     username: str = None,
                     is_first_node=False):
            self.username = username
            self.connection = connection
            self.cursor = database_cursor
            self.memory_cursor = memory_cursor
            self.memory_connection = memory_connection
            self.table_name = 'Blockchain'
            self.general_val_table = general_val_table
            self.current_block_id = None  # temporary after create_table() it will change
            self.block_to_calc_proof_of_work = None
            self.create_table()

            # TODO: intruduce my user by uploading a block
            #  that has the user in the new users part

            self.orphans_list = []  # list of all that has no origin

        def calculate_security_number_threshold(self) -> int:
            # TODO
            return 5

        def __insert_block_just_to_memory(self, block: Block):
            """used only in create table func """
            list_of_new_users_as_str = [user.as_str() for user in block.list_of_new_users]
            list_of_transactions_as_str = [tran.as_str() for tran in block.list_of_transactions]

            command = f'''INSERT INTO Blockchain VALUES ({block.id},{block.parent_id},{block.sequence_number},{block.level},{block.security_number},"{block.uploader_username}","{block.last_block_hash}","{block.current_block_hash}","{block.proof_of_work}","{block.timestamp}",'{json.dumps(list_of_transactions_as_str)}','{json.dumps(list_of_new_users_as_str)}')'''
            self.memory_cursor.execute(command)

        def insert_block(self, block: Block):
            """
            this function is called only after it had been confirmed that the block has a father in the blockchain
            """
            if self.current_block_id != block.id:
                raise Exception('something ain''t right')

            list_of_new_users_as_str = [user.as_str() for user in block.list_of_new_users]
            list_of_transactions_as_str = [tran.as_str() for tran in block.list_of_transactions]

            # TODO: delete
            # for user in block.list_of_new_users:
            #     list_of_new_users_as_str.append(user.as_str())
            # for tran in block.list_of_transactions:
            #     list_of_transactions_as_str.append(tran.as_str())

            command = f'''INSERT INTO Blockchain VALUES ({block.id},{block.parent_id},{block.sequence_number},{block.level},{block.security_number},"{block.uploader_username}","{block.last_block_hash}","{block.current_block_hash}","{block.proof_of_work}","{block.timestamp}",'{json.dumps(list_of_transactions_as_str)}','{json.dumps(list_of_new_users_as_str)}')'''
            self.cursor.execute(command)
            self.memory_cursor.execute(command)
            self.current_block_id += 1

        def increase_block_security_number(self, blocks_id: int):
            """
             increase security number by 1
            """
            command = f'''UPDATE Blockchain SET SecurityNumber = SecurityNumber + 1 WHERE ID = {blocks_id} '''
            self.cursor.execute(command)
            self.memory_cursor.execute(command)

        def create_genesis_block(self):
            genesis_block = Block('genesis', [], [], '', '')
            genesis_block.set_table_parameters(self.current_block_id, 0, 1, 0)
            self.block_to_calc_proof_of_work = genesis_block
            self.insert_block(genesis_block)

        def create_table(self):
            self.cursor.execute(f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';''')
            result = len(self.cursor.fetchall())
            create_table_command = f'''CREATE TABLE  {self.table_name} (ID INTEGER UNIQUE,ParentId INTEGER,SequenceNumber INTEGER,Level INTEGER,SecurityNumber INTEGER,UploaderUsername VARCHAR(256),LBH VARCHAR(257),CBH VARCHAR(257),POW VARCHAR(257), TimeStamp VARCHAR(255),LOT JSON,LONW JSON);'''
            if result == 0:  # aka table does not exist
                self.cursor.execute(create_table_command)
                self.memory_cursor.execute(create_table_command)

                self.current_block_id = 1  # default
                self.create_genesis_block()
            elif result == 1:  # aka table already exist

                # copying the table that already exist to  a table o memory{
                self.memory_cursor.execute(create_table_command)
                q = f'''SELECT * FROM Blockchain WHERE Level > {self.general_val_table.get_last_level_processed()}'''
                self.cursor.execute(q)
                list_of_all_blocks_to_memory_as_tup = self.cursor.fetchall()
                list_of_all_blocks_to_memory_block = [Block.create_block_from_tuple(x) for x in
                                                      list_of_all_blocks_to_memory_as_tup]

                for block in list_of_all_blocks_to_memory_block:
                    self.__insert_block_just_to_memory(block)
                # }

                # setting the current block id {
                self.memory_cursor.execute(f'''Select MAX(ID) From Blockchain''')
                max_id_list = self.memory_cursor.fetchall()
                if len(max_id_list) != 1:
                    raise Exception("duplicate max id")
                max_id = max_id_list[0][0]
                print(f'max id is {max_id}')
                self.current_block_id = max_id + 1
                # }

                # setting the block to clac POW{
                self.memory_cursor.execute('SELECT MAX(Level) FROM Blockchain')  # TODO
                max_level_list = self.memory_cursor.fetchall()
                max_level = max_level_list[0][0]  # getting the max level
                command = f'SELECT * FROM Blockchain WHERE Level = {max_level}'
                self.memory_cursor.execute(command)
                list_of_blocks_in_last_level = self.memory_cursor.fetchall()
                self.block_to_calc_proof_of_work = Block.create_block_from_tuple(
                    list_of_blocks_in_last_level[0])  # randomly choosing the first block
                # }

            else:
                raise Exception('duplicate tables')

    class UsersTable:
        MAX_BALANCE_DIGIT_LEN = 10
        MAX_BALANCE_DIGIT_LEN_AFTER_DOT = 10
        """
        the users table consist of a table that has three parameters
        username|publicKey|balance
        """""

        def __init__(self, database_cursor: sqlite3.Cursor, connection: sqlite3.Connection, username: str = None,
                     is_first_node=False):
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

        def is_user_exist(self, username) -> bool:
            self.cursor.execute(f'''SELECT * FROM {self.table_name} WHERE Username='{username}';''')
            rows = self.cursor.fetchall()
            return not len(rows) == 0

        def get_public_key(self, username: str):
            self.cursor.execute(f'''SELECT PublicKey FROM {self.table_name} WHERE Username='{username}';''')
            rows = self.cursor.fetchall()
            return rows[0][0]

        def add_user(self, user: User):
            s = f'''INSERT INTO {self.table_name} (Username, PublicKey, Balance) VALUES('{user.username}','{user.pk}',
            '{user.balance}');'''
            try:
                self.cursor.execute(s)
            except sqlite3.IntegrityError as e:
                print(e)
                pass

        def update_balance(self, username: str, new_balance):
            s = f'''UPDATE {self.table_name} SET Balance = {new_balance} WHERE Username = '{username}' '''
            self.cursor.execute(s)

        def make_transaction(self, transaction: Transaction):
            command = f'''SELECT * FROM {self.table_name} WHERE Username  = '{transaction.sender_username}' '''
            self.cursor.execute(command)
            tup = self.cursor.fetchall()[0]
            sender = User(tup[0], tup[1], int(tup[2]))

            command = f'''SELECT * FROM {self.table_name} WHERE Username  = '{transaction.receiver_username}' '''
            self.cursor.execute(command)
            tup = self.cursor.fetchall()[0]
            receiver = User(tup[0], tup[1], int(tup[2]))

            if sender.balance - transaction.amount < 0:
                return  # aka not enough money

            # TODO: check digital signature of both users{
            #  }

            # changing the users balance{
            self.update_balance(sender.username, sender.balance - transaction.amount)
            self.update_balance(receiver.username, receiver.balance + transaction.amount)
            # }

    def __init__(self, username: str, is_first_node: bool):  # TODO: maybe delete is first node
        """
        :param username: username of the database
        """
        self.username = username
        self.database_name = username
        self.__connection, self.__memory_connection = self.connect_to_db()
        self.__cursor, self.__memory_cursor = self.__connection.cursor(), self.__memory_connection.cursor()
        self.__lock = threading.Lock()
        self.general_val_table = self.GeneralVariablesTable(self.__cursor, self.__connection)
        self.users_table = self.UsersTable(self.__cursor, self.__connection)
        self.blockchain_table = self.BlockchainTable(self.__cursor, self.__connection, self.__memory_cursor,
                                                     self.__memory_connection, self.general_val_table)

        self.reward_for_block = 2  # TODO: currntly a temp value need to calculacte
        self.proof_of_work_difficulty = 15  # TODO: currntly a temp value need to calculacte
        self.pow_target = 12  # TODO: currntly a temp value need to calculacte

    def connect_to_db(self):
        return sqlite3.connect(f'{self.username}.db', check_same_thread=False), sqlite3.connect(':memory:',
                                                                                                check_same_thread=False)

    def acquire(self):
        self.__lock.acquire()

    def release(self):
        self.__connection.commit()
        self.__memory_connection.commit()
        self.__lock.release()

    def close(self):
        self.__connection.commit()
        self.__memory_connection.commit()
        self.__connection.close()
        self.__memory_connection.close()

    def print_data(self):
        command = f'''SELECT * FROM Blockchain'''
        self.__cursor.execute(command)
        self.__memory_cursor.execute(command)
        result = self.__cursor.fetchall()
        result_memory = self.__memory_cursor.fetchall()
        command = f'''SELECT  * FROM Users'''
        self.__cursor.execute(command)
        result_users = self.__cursor.fetchall()
        print(f'result {result}\nresult_memory {result_memory}\nresult_users {result_users}')

    def process_block(self, block: Block):
        """
        this function will be called every time a block has passed the threshold to be considered secure
        then and only then the block content will be taken in to account

        when prosseisng a block you need to first of all him and then to add all of the ney users to the table
        in order to solve situations that the uploader is a new user
        :return:
        """
        if block.uploader_username == 'genesis':
            return
            # add all new users{
        for user in block.list_of_new_users:
            self.users_table.add_user(user)
        # }

        # TODO: give reward to the block owner{

        current_balance = self.users_table.get_balance(block.uploader_username)
        self.users_table.update_balance(block.uploader_username, current_balance + self.reward_for_block)
        # }

        # TODO: handle all transactions {
        for transaction in block.list_of_transactions:
            self.users_table.make_transaction(transaction)
        # }

    def add_block(self, block: Block) -> AddBlockStatus:
        """
        all the checking is using the memory table but every change is being done to both tables
        :param block: the block to add to the database
        :return: a string that says what happened inside the function
        """

        # check if block hash match  {
        if block.current_block_hash != block.compute_hash():
            print('invalid hash')
            return AddBlockStatus.INVALID_BLOCK

        # }

        # check if the block has a father
        self.blockchain_table.memory_cursor.execute(
            f'''SELECT * FROM Blockchain WHERE CBH = '{block.last_block_hash}' ''')
        list_of_fathers = self.blockchain_table.memory_cursor.fetchall()
        if len(list_of_fathers) == 0:  # aka block is an orphan
            self.blockchain_table.orphans_list.append(block)
            print('orphan')
            return AddBlockStatus.ORPHAN_BLOCK

        elif len(list_of_fathers) == 1:  # aka found a father
            father = list_of_fathers[0]
            father = Block.create_block_from_tuple(father)
            # check pow{
            target = 2 ** (256 - self.proof_of_work_difficulty)
            input_to_hash = father.as_str() + str(block.proof_of_work)

            hash_result = hashlib.sha256(input_to_hash.encode()).hexdigest()
            if int(hash_result, 16) >= target:  # aka proof of work is not good
                print('invalid pow')
                return AddBlockStatus.INVALID_BLOCK
            # }

            # add the block to the table
            my_id = self.blockchain_table.current_block_id
            my_parent_id = father.id
            my_sequence_number = 0  # TODO
            my_level = father.level + 1
            my_security_number = 0
            block.set_table_parameters(my_id, my_parent_id, my_sequence_number, my_level, my_security_number)
            self.blockchain_table.insert_block(block)
            # }

            # {
            if block.level > self.blockchain_table.block_to_calc_proof_of_work.level:
                self.blockchain_table.block_to_calc_proof_of_work = block
            # }

            self.blockchain_table.memory_cursor.execute(
                f'''SELECT ID FROM Blockchain WHERE ParentId = {my_parent_id}''')
            list_of_brothers = self.blockchain_table.memory_cursor.fetchall()

            if len(list_of_brothers) == 1:  # aka i am the first son
                """
                here there are two options 
                1: I run and Update both the memory table and the one in the db but i stop when the updating finshed
                   on the memory table. it will be faster and more efficient 
                2: I do the same thing but i stop when the table in the db is finished (also the table on memory will finish).
                   It will take more time and as the chain keeps growing the time will increase in a liner line

                for now i choose option 1 but i am open for change
                """
                current_block = block
                while True:
                    command = f'''SELECT * FROM Blockchain WHERE ID = {current_block.parent_id} '''
                    self.blockchain_table.memory_cursor.execute(command)
                    father_block_list = self.blockchain_table.memory_cursor.fetchall()
                    if len(father_block_list) == 0:  # aka  I finished to update the entire memory table
                        break
                    elif len(father_block_list) == 1:
                        father_block = Block.create_block_from_tuple(father_block_list[0])
                        self.blockchain_table.increase_block_security_number(father_block.id)
                        current_block = father_block
                    else:
                        raise Exception('block has an unexpected amount of fathers')

                #  check if any blocks has passed the security threshold
                #  and remove any block that has an equal \ lower level the them{

                command = f'''SELECT * FROM Blockchain WHERE SecurityNumber > {self.blockchain_table.calculate_security_number_threshold()} '''
                self.blockchain_table.memory_cursor.execute(command)
                list_of_blocks_that_need_to_be_processed = self.blockchain_table.memory_cursor.fetchall()
                len_of_list_of_blocks_that_need_to_be_processed = len(list_of_blocks_that_need_to_be_processed)
                if len_of_list_of_blocks_that_need_to_be_processed == 0:
                    pass
                elif len_of_list_of_blocks_that_need_to_be_processed == 1:
                    block_to_process = Block.create_block_from_tuple(list_of_blocks_that_need_to_be_processed[0])
                    self.process_block(block_to_process)
                    self.general_val_table.set_last_level_processed(block_to_process.level)
                    # remove blocks that  became irrelevant
                    command = f'''SELECT * FROM Blockchain WHERE Level <= {block_to_process.level} '''
                    self.blockchain_table.memory_cursor.execute(command)
                    l = self.blockchain_table.memory_cursor.fetchall()
                    for i in l:
                        print(f"deleting block {i[5]}")
                    command = f'''DELETE FROM Blockchain WHERE Level <= {block_to_process.level} '''
                    self.blockchain_table.memory_cursor.execute(command)
                else:
                    raise Exception('more then one block has passed the threshold')
                # }
            elif len(list_of_brothers) > 1:  # aka i am not the first son
                pass  # TODO: see if updating the SequenceNumber is relevant
            else:
                raise Exception(f'an unexpected amount of sons {len(list_of_brothers)}')

            # check the orphan list
            for orphan_block in self.blockchain_table.orphans_list:
                if orphan_block.last_block_hash == block.current_block_hash:
                    self.blockchain_table.orphans_list.remove(orphan_block)
                    self.add_block(orphan_block)
        else:
            raise Exception('block has an unexpected amount of fathers')
