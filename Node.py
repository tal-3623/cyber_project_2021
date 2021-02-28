import json
import socket
import threading

from Constants import *
from Message import MessageBetweenNodes
from MessageType import MessageTypeBetweenNodes
from ServerDatabase import ServerDatabase


class Node:

    def __init__(self, username: str, port_for_nodes: int, port_for_clients: int,
                 node_to_connect_through=None):

        self.username = username
        self.server_database = ServerDatabase(username)
        self.lock = threading.Lock()
        self.list_of_nodes = []
        self.list_of_clients = []
        self.list_of_transactions_to_make = []
        self.block_to_upload = None
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

            nodes_address_received = json.loads(msg.content)

            self.list_of_nodes.append(node_address)
            t = threading.Thread(target=self.handle_node, args=(temp_sock, node_address,))
            t.start()
            for node_address in nodes_address_received:
                if node_address in self.list_of_nodes:
                    continue
                node_address = tuple(node_address)
                sock = socket.socket()
                sock.connect(node_address)
                # TODO check : sends new connction msg
                msg = MessageBetweenNodes(MessageTypeBetweenNodes.NewConnection, str(self.__port_for_nodes))
                msg.send(sock)
                self.list_of_nodes.append(node_address)
                t = threading.Thread(target=self.handle_node, args=(sock, node_address,))
                t.start()

        except ConnectionRefusedError or socket.timeout as e:
            print(e)
            print("the server to connect through is offline!")
            # TODO decide what to do when the  server to connect through is offline
            raise Exception("stop")

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
        self.list_of_nodes.append(address)
        address_list = []
        for node in self.list_of_nodes:
            if address == node:
                continue
            address_list.append(node)
        json_string = json.dumps(address_list)
        msg = MessageBetweenNodes(message_type=MessageTypeBetweenNodes.newServerDataTransfer, content=json_string)
        msg.send(sock)
        return address

    def handle_get_blocks(self, content, sock: socket.socket):
        pass  # TODO

    def handle_new_block(self, content):
        pass  # TODO

    def handle_new_connection(self, content, address):
        port_of_other_node = int(content)
        ip_of_other_node = address[0]
        address = (ip_of_other_node, port_of_other_node)
        if address not in self.list_of_nodes:
            self.list_of_nodes.append(address)
        return address

    def handle_node(self, node_socket: socket, address: tuple):
        node_socket.settimeout(SOCKET_RECEIVE_TIMEOUT)
        try:
            while True:
                try:
                    msg = MessageBetweenNodes()
                    msg.recv(node_socket)
                    self.lock.acquire()
                    if msg.message_type == MessageTypeBetweenNodes.newServerDataRequest:
                        address = self.handle_new_server_data_request(msg.content, node_socket, address)
                    elif msg.message_type == MessageTypeBetweenNodes.LogOff:
                        self.handle_log_off(msg.content)
                    elif msg.message_type == MessageTypeBetweenNodes.getBlocks:
                        self.handle_get_blocks(msg.content, node_socket)
                    elif msg.message_type == MessageTypeBetweenNodes.NewBlock:
                        self.handle_new_block(msg.content)
                    elif msg.message_type == MessageTypeBetweenNodes.NewConnection:
                        address = self.handle_new_connection(msg.content, address)
                    else:
                        raise Exception('unexpected message')

                    self.lock.release()
                except socket.timeout:
                    pass

                self.lock.acquire()
                if self.block_to_upload is not None:
                    pass
                    # TODO: send new block message
                self.lock.release()

        except ConnectionError as e:
            # remove node from list of online nodes
            self.lock.acquire()
            self.list_of_nodes.remove(address)
            self.lock.release()

    def run(self):
        while True:
            print(self.list_of_nodes)
            # add a client
            try:
                client_socket, address = self.socket_for_clients.accept()
                self.list_of_clients.append((client_socket, address))
                t = threading.Thread(target=self.handle_client, args=(client_socket, address,))
                t.start()
            except socket.timeout:
                pass

            # add a node
            try:
                node_socket, address = self.socket_for_nodes.accept()
                t = threading.Thread(target=self.handle_node, args=(node_socket, address,))
                t.start()
            except socket.timeout:
                pass
