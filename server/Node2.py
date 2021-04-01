import hashlib
import json
import socket
import threading
import time
from random import randint

from Constants import *
from server.AddBlockStatus import AddBlockStatus
from server.ClientState import ClientState
from server.ServerDatabase import ServerDatabase
from utill.blockchain.Block import Block
from utill.blockchain.Transaction import Transaction
from utill.blockchain.User import User
from utill.encription.EncriptionKey import Key
from utill.network.Message import MessageBetweenNodes, MessageBetweenNodeAndClient
from utill.network.MessageType import MessageType


class Node:

    def __init__(self, user: User, user_private_key: Key, port_for_nodes: int, port_for_clients: int,
                 node_to_connect_through=None):

        self.username = user.username
        self.user = user
        is_this_first_node = node_to_connect_through is Node
        self.server_database = ServerDatabase(user.username, is_this_first_node)
        self.__lock = threading.Lock()
        self.list_of_nodes_address = []
        self.list_of_nodes_sockets = []
        self.dict_of_clients_and_usernames = {}
        self.dict_of_clients_and_usernames_waiting_for_confirmation = {}
        self.list_of_transactions_to_make = []
        self.list_of_transactions_to_make_waiting_to_be_processed = []
        self.list_of_new_users_to_upload = []
        self.list_of_new_users_to_upload_waiting_to_be_processed = []
        self.is_user_been_processed = False

        self.block_to_upload = None
        # self.block_to_calc_proof_of_work = self.server_database.blockchain_table.block_to_calc_proof_of_work
        self.__port_for_nodes = port_for_nodes
        self.__port_for_clients = port_for_clients

        self.socket_for_nodes = socket.socket()
        self.socket_for_nodes.bind(('0.0.0.0', port_for_nodes))
        self.socket_for_nodes.listen(MAX_NODES_CONNECTION)
        self.socket_for_nodes.settimeout(SOCKET_ACCEPT_TIMEOUT)

        self.socket_for_clients = socket.socket()
        self.socket_for_clients.bind(('0.0.0.0', port_for_clients))
        self.socket_for_clients.listen(MAX_CLIENTS_CONNECTION)
        self.socket_for_clients.settimeout(SOCKET_ACCEPT_TIMEOUT)

        if node_to_connect_through is not None:  # not the first node in the network
            self.initialize(node_to_connect_through)

        else:  # -> first node of the network
            pass
            # TODO: create a new user

        if self.server_database.users_table.is_user_exist(user.username):
            self.is_user_been_processed = True

    def acquire(self):
        self.__lock.acquire()
        self.server_database.acquire()

    def release(self):
        self.__lock.release()
        self.server_database.release()

    def initialize(self, node_address) -> bool:
        '''

        :param node_address:
        :return: is init worked
        '''

        try:
            temp_sock = socket.socket()
            temp_sock.settimeout(10)
            temp_sock.connect(node_address)

            # TODO send newServerDataRequest
            msg = MessageBetweenNodes(MessageType.newServerDataRequest, str(self.__port_for_nodes))
            msg.send(temp_sock)

            # TODO receive newServerDataTransfer

            msg = MessageBetweenNodes()
            msg.recv(temp_sock)
            # TODO add all the the other nodes to list of nodes
            if msg.message_type != MessageType.newServerDataTransfer:
                raise Exception('got a diifrent msg then expected')
            nodes_address_received = json.loads(msg.content)

            self.list_of_nodes_address.append(node_address)
            self.list_of_nodes_sockets.append(temp_sock)
            t = threading.Thread(target=self.handle_node, args=(temp_sock, node_address,))
            t.start()
            for node_address in nodes_address_received:
                if node_address in self.list_of_nodes_address:
                    continue
                node_address = tuple(node_address)
                sock = socket.socket()
                sock.connect(node_address)
                # TODO check : sends new connction msg
                msg = MessageBetweenNodes(MessageType.NewConnection, str(self.__port_for_nodes))
                msg.send(sock)
                self.list_of_nodes_address.append(node_address)
                self.list_of_nodes_sockets.append(sock)
                t = threading.Thread(target=self.handle_node, args=(sock, node_address,))
                t.start()

        except ConnectionRefusedError or ConnectionError or socket.timeout as e:
            print(e)
            print("the server to connect through is offline!")
            # TODO decide what to do when the  server to connect through is offline
            raise Exception("the server to connect through is offline!")

    def handle_client(self, client_socket: socket):
        username = ''
        client_socket.settimeout(0.2)
        client_state = ClientState.NOT_LOGGED_IN
        try:
            while True:
                try:
                    self.acquire()
                    if client_state == ClientState.NOT_LOGGED_IN:
                        msg = MessageBetweenNodeAndClient()
                        client_socket.settimeout(SOCKET_CLIENT_RECEIVE_SHORT_TIMEOUT)
                        t = time.time()
                        msg.recv(client_socket)

                        client_socket.settimeout(SOCKET_CLIENT_RECEIVE_LONG_TIMEOUT)
                        if msg.message_type == MessageType.SIGN_UP:
                            list_of_data = json.loads(msg.content)
                            username, pk_as_str = list_of_data
                            pk = Key.create_from_str(pk_as_str)
                            # check if pk and username are taken and send result to client {
                            is_user_taken = self.server_database.users_table.is_user_exist(username)
                            is_pk_taken = self.server_database.users_table.is_public_key_exist(pk)
                            content = str(int(is_user_taken)) + str(int(is_pk_taken))
                            msg_to_send = MessageBetweenNodeAndClient(MessageType.SIGN_UP_ANSWER,
                                                                      content)
                            msg_to_send.send(client_socket)
                            # }

                            if not is_user_taken and not is_pk_taken:
                                pass  # add user to upload
                                user = User(username, pk)
                                self.list_of_new_users_to_upload.append(user)
                                self.dict_of_clients_and_usernames_waiting_for_confirmation[user] = client_socket
                                client_state = ClientState.WAITING_FOR_CONFIRMATION
                            else:
                                pass
                        elif msg.message_type == MessageType.LOG_IN_REQUEST:
                            username = msg.content
                            if not self.server_database.users_table.is_user_exist(username):
                                print(f'not user named {username}')
                                msg = MessageBetweenNodeAndClient(MessageType.LOG_IN_FAILED)
                                msg.send(client_socket)

                            random = str(randint(0, 10000))
                            msg = MessageBetweenNodeAndClient(MessageType.LOG_IN_RAND, random)
                            msg.send(client_socket)

                            msg.recv(client_socket)
                            if msg.message_type != MessageType.LOG_IN_RAND_ANSWER:
                                raise Exception('unxpexted msg')
                            client_pk = self.server_database.users_table.get_public_key(username)
                            if not client_pk.verify(msg.content, random):
                                msg = MessageBetweenNodeAndClient(MessageType.LOG_IN_FAILED)
                            else:
                                msg = MessageBetweenNodeAndClient(MessageType.LOG_IN_ACCEPTED)
                            msg.send(client_socket)
                            client_socket.settimeout(SOCKET_CLIENT_RECEIVE_SHORT_TIMEOUT)
                            self.dict_of_clients_and_usernames[username] = client_socket
                            client_state = ClientState.LOGGED_IN
                        else:
                            raise Exception('unxpexted msg')

                    elif client_state == ClientState.LOGGED_IN:
                        msg = MessageBetweenNodeAndClient()
                        msg.recv(client_socket)
                        if msg.message_type == MessageType.GET_ALL_TRANSACTIONS:
                            # serch the database for all transactions revolving the user {
                            tuples, current_amount_of_money = self.server_database.get_all_transactions_of(username)
                            print(f'current_amount_of_money {current_amount_of_money} (190)')
                            content = json.dumps(
                                [[(t[0].as_str(), t[1]) for t in tuples], str(current_amount_of_money)])
                            msg_to_send = MessageBetweenNodeAndClient(
                                MessageType.RECEIVE_ALL_TRANSACTIONS, content)
                            msg_to_send.send(client_socket)
                            # }
                        elif msg.message_type == MessageType.TRANSACTION_OFFERED:
                            transaction = Transaction.create_from_str(msg.content)
                            self.list_of_transactions_to_make.append(transaction)
                        elif msg.message_type == MessageType.TRANSACTION_COMPLETED:
                            transaction = Transaction.create_from_str(msg.content)
                            self.list_of_transactions_to_make.append(transaction)
                    elif client_state == ClientState.WAITING_FOR_CONFIRMATION:
                        if self.dict_of_clients_and_usernames_waiting_for_confirmation.get(user) is None:
                            client_socket.close()
                            self.release()
                            return

                    self.release()
                except socket.timeout:
                    self.release()


        except ConnectionError as e:
            print(e)
            print('nlafsdfdsfdsfds')
            self.release()
            return

    def send_transaction_to_clients_if_needed(self, transaction: Transaction):
        for username in list(self.dict_of_clients_and_usernames.keys()):
            if transaction.sender_username == username or transaction.receiver_username == username:
                if not self.server_database.users_table.is_user_exist(
                        transaction.sender_username) or not self.server_database.users_table.is_user_exist(
                    transaction.receiver_username):
                    return  # one of the users does not exist so so nothing
                sender = self.server_database.users_table.get_user(transaction.sender_username)
                receiver = self.server_database.users_table.get_user(transaction.receiver_username)

                if sender.balance - transaction.amount < 0:
                    print('not enough money')
                    return  # aka not enough money

                if transaction.is_signature_valid(sender.pk, receiver.pk):  # both valid
                    msg = MessageBetweenNodeAndClient(MessageType.TRANSACTION_COMPLETED,
                                                      transaction.as_str())
                elif transaction.receiver_username == username and transaction.is_sender_signature_valid(sender.pk):
                    msg = MessageBetweenNodeAndClient(MessageType.TRANSACTION_OFFERED,
                                                      transaction.as_str())
                else:
                    continue

                try:
                    msg.send(self.dict_of_clients_and_usernames[username])
                except ConnectionError:
                    self.dict_of_clients_and_usernames.pop(username)

    def send_block_upload_to_clients_if_needed(self, block: Block, reward_for_block: float):
        for username in list(self.dict_of_clients_and_usernames.keys()):
            if username == block.uploader_username:
                content = str(reward_for_block)
                msg = MessageBetweenNodeAndClient(MessageType.BLOCK_UPLOADED, content)
                try:
                    msg.send(self.dict_of_clients_and_usernames[username])
                except ConnectionError:
                    self.dict_of_clients_and_usernames.pop(username)

    # ----------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------

    def handle_log_off(self, content):
        pass

    def handle_new_server_data_request(self, content, sock: socket.socket, address):
        '''
        :param content:
        :param sock:
        :param address:
        :return: sends newServerDataTransfer
        '''
        port_of_other_node = int(content)
        ip_of_other_node = address[0]
        address = (ip_of_other_node, port_of_other_node)
        self.list_of_nodes_address.append(address)
        address_list = []
        for node in self.list_of_nodes_address:
            if address == node:
                continue
            address_list.append(node)
        json_string = json.dumps(address_list)
        msg = MessageBetweenNodes(message_type=MessageType.newServerDataTransfer, content=json_string)
        msg.send(sock)
        return address

    def handle_get_blocks(self, content, socket: socket.socket):
        block_received = Block.create_block_from_tuple_received(json.loads(content))
        father = self.server_database.blockchain_table.get_father(block_received)
        if father is not None:
            content = father.as_str_to_send()
            msg = MessageBetweenNodes(MessageType.NewBlock, content)
            msg.send(socket)
        else:
            raise Exception(f'got get block msg for a block that i dont have a father')

    def handle_new_block(self, content: str, socket: socket.socket):
        print('296', content)
        new_block_as_tup = json.loads(content)
        new_block = Block.create_block_from_tuple_received(new_block_as_tup)
        add_block_result = self.server_database.add_block(new_block, self)
        # print(f"add_block_result (in new) {add_block_result.name}")
        if add_block_result == AddBlockStatus.INVALID_BLOCK:
            pass
        elif add_block_result == AddBlockStatus.ORPHAN_BLOCK:
            content = new_block.as_str_to_send()
            msg = MessageBetweenNodes(MessageType.getBlocks, content)  # TODO send get blocks
            msg.send(socket)
        else:
            pass

    def handle_new_connection(self, content, address):
        port_of_other_node = int(content)
        ip_of_other_node = address[0]
        address = (ip_of_other_node, port_of_other_node)
        if address not in self.list_of_nodes_address:
            self.list_of_nodes_address.append(address)
        return address

    def handle_node(self, node_socket: socket.socket, address: tuple):
        node_socket.settimeout(SOCKET_RECEIVE_TIMEOUT)
        try:
            while True:
                try:
                    self.acquire()
                    msg = MessageBetweenNodes()
                    msg.recv(node_socket)
                    if msg.message_type == MessageType.newServerDataRequest:
                        address = self.handle_new_server_data_request(msg.content, node_socket, address)
                    elif msg.message_type == MessageType.LogOff:
                        self.handle_log_off(msg.content)  # TODO log off
                    elif msg.message_type == MessageType.getBlocks:
                        self.handle_get_blocks(msg.content, node_socket)  # TODO get blocks
                    elif msg.message_type == MessageType.NewBlock:
                        self.handle_new_block(msg.content, node_socket)  # TODO: new block
                    elif msg.message_type == MessageType.NewConnection:
                        address = self.handle_new_connection(msg.content, address)
                    else:
                        # raise Exception('unexpected message')
                        print('unexpected message')
                    self.release()
                except socket.timeout:
                    self.release()

        except ConnectionError as e:
            # raise e
            # remove node from list of online nodes
            print(f' self.list_of_nodes_address {self.list_of_nodes_address}')
            print(f'adress {address}')
            try:
                self.list_of_nodes_address.remove(address)
                self.list_of_nodes_sockets.remove(node_socket)
            except ValueError:
                print('351 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            self.release()

    def find_proof_of_work_and_upload_block(self):
        self.acquire()
        block = self.server_database.blockchain_table.block_to_calc_proof_of_work
        proof_of_work_difficulty = self.server_database.proof_of_work_difficulty
        self.release()
        while True:

            target = 2 ** (256 - proof_of_work_difficulty)
            print(f'frec is {(2 ** proof_of_work_difficulty) // PROOF_OF_WORK_CHECK_BLOCK_FREQUENCY}')
            for nonce in range(MAX_NONCE):
                if nonce % (2 ** proof_of_work_difficulty) // PROOF_OF_WORK_CHECK_BLOCK_FREQUENCY == 0:  # 2^diff =
                    # average amount of tries before success,PROOF_OF_WORK_CHECK_BLOCK_FREQUENCY is how many times to
                    # check if it took the avg tries
                    self.acquire()
                    if block != self.server_database.blockchain_table.block_to_calc_proof_of_work:
                        self.block_to_upload = None
                        block = self.server_database.blockchain_table.block_to_calc_proof_of_work
                        self.release()
                        break
                    self.release()
                input_to_hash = block.as_str() + str(nonce)
                hash_result = hashlib.sha256(input_to_hash.encode()).hexdigest()

                if int(hash_result, 16) < target:
                    print(nonce, 'nonce is !!')
                    self.acquire()
                    if block != self.server_database.blockchain_table.block_to_calc_proof_of_work:
                        self.block_to_upload = None
                        block = self.server_database.blockchain_table.block_to_calc_proof_of_work
                        self.release()
                        break

                    # build block to upload {
                    x = min(len(self.list_of_transactions_to_make),
                            MAX_LEN_OF_LIST_OF_TRANSACTIONS)
                    list_of_transactions_to_make = self.list_of_transactions_to_make[:x]  # all tran in this block
                    self.list_of_transactions_to_make_waiting_to_be_processed.extend(list_of_transactions_to_make)
                    self.list_of_transactions_to_make = self.list_of_transactions_to_make[x:]

                    x = min(len(self.list_of_new_users_to_upload),
                            MAX_LEN_OF_LIST_OF_NEW_USERS)
                    if not self.is_user_been_processed:
                        list_of_new_users_to_upload = [self.user]
                    else:
                        list_of_new_users_to_upload = []
                    list_of_new_users_to_upload.extend(self.list_of_new_users_to_upload[:x])

                    self.list_of_new_users_to_upload_waiting_to_be_processed.extend(
                        list_of_new_users_to_upload)
                    self.list_of_new_users_to_upload = self.list_of_new_users_to_upload[
                                                       x:]

                    # print(f'uploading block with {[t.as_str() for t in list_of_transactions_to_make]}')
                    last_block_hash = block.current_block_hash
                    self.block_to_upload = Block(self.username, list_of_transactions_to_make,
                                                 list_of_new_users_to_upload,
                                                 last_block_hash)
                    self.block_to_upload.proof_of_work = nonce
                    # }

                    # send block to all nodes{
                    result = self.server_database.add_block(self.block_to_upload, self)
                    if result == AddBlockStatus.INVALID_BLOCK:
                        Exception('i uploaded invalid')
                    elif result == AddBlockStatus.ORPHAN_BLOCK:
                        Exception('i uploaded orphan')
                    elif result == AddBlockStatus.SUCCESSFUL:
                        content = self.block_to_upload.as_str_to_send()
                        msg_to_send = MessageBetweenNodes(MessageType.NewBlock, content)
                        for sock in self.list_of_nodes_sockets:
                            try:
                                msg_to_send.send(sock)
                            except Exception as e:
                                pass
                            # TODO: send new block message
                    self.block_to_upload = None
                    self.release()
                    # }

    def run(self):
        t = threading.Thread(target=self.find_proof_of_work_and_upload_block, args=())
        t.start()

        socket_for_clients = self.socket_for_clients
        socket_for_nodes = self.socket_for_nodes

        while True:

            # add a client
            try:
                client_socket, address = socket_for_clients.accept()
                self.acquire()
                # self.dict_of_clients_and_usernames
                t = threading.Thread(target=self.handle_client, args=(client_socket,))
                t.start()
                self.release()
            except socket.timeout:
                pass

            # add a node
            try:
                node_socket, address = socket_for_nodes.accept()
                self.acquire()
                self.list_of_nodes_sockets.append(node_socket)
                t = threading.Thread(target=self.handle_node, args=(node_socket, address,))
                self.release()
                t.start()
            except socket.timeout:
                pass
