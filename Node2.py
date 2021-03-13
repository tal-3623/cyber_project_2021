import hashlib
import json
import socket
import threading
import time

from AddBlockStatus import AddBlockStatus
from Block import Block
from Constants import *
from Message import MessageBetweenNodes
from MessageType import MessageTypeBetweenNodes
from ServerDatabase import ServerDatabase
from User import User


class Node:

    def __init__(self, user: User, port_for_nodes: int, port_for_clients: int,
                 node_to_connect_through=None):

        self.username = user.username
        self.user = user
        is_this_first_node = node_to_connect_through is Node
        self.server_database = ServerDatabase(user.username, is_this_first_node)
        self.__lock = threading.Lock()
        self.list_of_nodes_address = []
        self.list_of_nodes_sockets = []
        self.list_of_clients = []
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
            msg = MessageBetweenNodes(MessageTypeBetweenNodes.newServerDataRequest, str(self.__port_for_nodes))
            msg.send(temp_sock)

            # TODO receive newServerDataTransfer

            msg = MessageBetweenNodes()
            msg.recv(temp_sock)
            # TODO add all the the other nodes to list of nodes
            if msg.message_type != MessageTypeBetweenNodes.newServerDataTransfer:
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
                msg = MessageBetweenNodes(MessageTypeBetweenNodes.NewConnection, str(self.__port_for_nodes))
                msg.send(sock)
                self.list_of_nodes_address.append(node_address)
                self.list_of_nodes_sockets.append(sock)
                t = threading.Thread(target=self.handle_node, args=(sock, node_address,))
                t.start()

        except ConnectionRefusedError or socket.timeout as e:
            print(e)
            print("the server to connect through is offline!")
            # TODO decide what to do when the  server to connect through is offline
            raise Exception("the server to connect through is offline!")

    def handle_client(self, client_socket: socket, address):
        pass

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
        msg = MessageBetweenNodes(message_type=MessageTypeBetweenNodes.newServerDataTransfer, content=json_string)
        msg.send(sock)
        return address

    def handle_get_blocks(self, content, socket: socket.socket):
        print(f'in get blocks')
        block_received = Block.create_block_from_tuple_received(json.loads(content))
        father = self.server_database.blockchain_table.get_father(block_received)
        if father is not None:
            content = father.as_str_to_send()
            msg = MessageBetweenNodes(MessageTypeBetweenNodes.NewBlock, content)
            msg.send(socket)
        else:
            self.server_database.print_data()
            raise Exception(f'got get block msg for a block that i dont have a father')

    def handle_new_block(self, content: str, socket: socket.socket):
        print('in handle_new_block')
        new_block_as_tup = json.loads(content)
        new_block = Block.create_block_from_tuple_received(new_block_as_tup)
        add_block_result = self.server_database.add_block(new_block, self)
        print(f'{add_block_result.name}')
        if add_block_result == AddBlockStatus.INVALID_BLOCK:
            pass
        elif add_block_result == AddBlockStatus.ORPHAN_BLOCK:
            content = new_block.as_str_to_send()
            msg = MessageBetweenNodes(MessageTypeBetweenNodes.getBlocks, content)  # TODO send get blocks
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
                    print(msg.message_type.name, msg.content)
                    if msg.message_type == MessageTypeBetweenNodes.newServerDataRequest:
                        address = self.handle_new_server_data_request(msg.content, node_socket, address)
                    elif msg.message_type == MessageTypeBetweenNodes.LogOff:
                        self.handle_log_off(msg.content)  # TODO log off
                    elif msg.message_type == MessageTypeBetweenNodes.getBlocks:
                        self.handle_get_blocks(msg.content, node_socket)  # TODO get blocks
                    elif msg.message_type == MessageTypeBetweenNodes.NewBlock:
                        self.handle_new_block(msg.content, node_socket)  # TODO: new block
                    elif msg.message_type == MessageTypeBetweenNodes.NewConnection:
                        address = self.handle_new_connection(msg.content, address)
                    else:
                        raise Exception('unexpected message')
                    self.release()
                except socket.timeout:
                    self.release()

        except ConnectionError as e:
            # raise e
            # remove node from list of online nodes
            print(f' self.list_of_nodes_address { self.list_of_nodes_address}')
            print(f'adress {address}')
            self.list_of_nodes_address.remove(address)
            self.list_of_nodes_sockets.remove(node_socket)
            self.release()

    def find_proof_of_work_and_upload_block(self):
        self.acquire()
        block = self.server_database.blockchain_table.block_to_calc_proof_of_work
        proof_of_work_difficulty = self.server_database.proof_of_work_difficulty
        self.release()
        while True:

            # # testing {
            # self.acquire()
            # self.release()
            # # }

            print('in start of while true')
            target = 2 ** (256 - proof_of_work_difficulty)
            for nonce in range(MAX_NONCE):
                if nonce % PROOF_OF_WORK_CHECK_BLOCK_FREQUENCY == 0:
                    self.acquire()
                    if block != self.server_database.blockchain_table.block_to_calc_proof_of_work:
                        self.block_to_upload = None
                        print('someone else solved block before me')
                        block = self.server_database.blockchain_table.block_to_calc_proof_of_work
                        self.release()
                        break
                    self.release()
                input_to_hash = block.as_str() + str(nonce)
                hash_result = hashlib.sha256(input_to_hash.encode()).hexdigest()

                if int(hash_result, 16) < target:
                    self.acquire()
                    if block != self.server_database.blockchain_table.block_to_calc_proof_of_work:
                        self.block_to_upload = None
                        print('someone else solved block before me')
                        block = self.server_database.blockchain_table.block_to_calc_proof_of_work
                        self.release()
                        break

                    # build block to upload {
                    x = max(len(self.list_of_transactions_to_make),
                            MAX_LEN_OF_LIST_OF_TRANSACTIONS)
                    list_of_transactions_to_make = self.list_of_transactions_to_make[:x]  # all tran in this block
                    self.list_of_transactions_to_make_waiting_to_be_processed.extend(list_of_transactions_to_make)
                    self.list_of_transactions_to_make = self.list_of_transactions_to_make[x:]

                    x = max(len(self.list_of_new_users_to_upload),
                            MAX_LEN_OF_LIST_OF_NEW_USERS)
                    if not self.is_user_been_processed:
                        list_of_new_users_to_upload = [self.user]
                    else:
                        list_of_new_users_to_upload = []
                    list_of_new_users_to_upload.extend(self.list_of_new_users_to_upload[:x])

                    self.list_of_new_users_to_upload_waiting_to_be_processed.extend(list_of_new_users_to_upload)
                    self.list_of_new_users_to_upload = self.list_of_new_users_to_upload[x:]

                    last_block_hash = block.current_block_hash
                    self.block_to_upload = Block(self.username, list_of_transactions_to_make,
                                                 list_of_new_users_to_upload,
                                                 last_block_hash)
                    self.block_to_upload.proof_of_work = nonce
                    # }

                    # send block to all nodes{
                    print(f'finished {self.block_to_upload.as_str_to_send()}')
                    result = self.server_database.add_block(self.block_to_upload, self)
                    print(f'result is {result.name}')
                    if result == AddBlockStatus.INVALID_BLOCK:
                        Exception('i uploaded invalid')
                    elif result == AddBlockStatus.ORPHAN_BLOCK:
                        Exception('i uploaded orphan')
                    elif result == AddBlockStatus.SUCCESSFUL:
                        content = self.block_to_upload.as_str_to_send()
                        msg_to_send = MessageBetweenNodes(MessageTypeBetweenNodes.NewBlock, content)
                        print(self.list_of_nodes_sockets)
                        for sock in self.list_of_nodes_sockets:
                            try:
                                msg_to_send.send(sock)
                            except Exception as e:
                                print(e)
                            # TODO: send new block message
                    self.block_to_upload = None
                    self.release()
                    # }

    def run(self):
        t = threading.Thread(target=self.find_proof_of_work_and_upload_block, args=())
        t.start()

        while True:
            # # testing{
            # self.acquire()
            # # print(self.list_of_nodes_address)
            # # print(self.list_of_nodes_sockets)
            # print([a.as_str() for a in self.list_of_new_users_to_upload])
            # print([a.as_str() for a in self.list_of_new_users_to_upload_waiting_to_be_processed])
            # print([a.as_str() for a in self.list_of_transactions_to_make])
            # print([a.as_str() for a in self.list_of_transactions_to_make_waiting_to_be_processed])
            # self.release()
            # # }

            socket_for_clients = self.socket_for_clients
            socket_for_nodes = self.socket_for_nodes
            # add a client
            try:
                client_socket, address = socket_for_clients.accept()
                self.acquire()
                self.list_of_clients.append((client_socket, address))
                t = threading.Thread(target=self.handle_client, args=(client_socket, address,))
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
                t.start()
                self.release()
            except socket.timeout:
                pass
