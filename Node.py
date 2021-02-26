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
            temp_sock.connect((node_address[0], node_address[1]))

            # TODO send newServerDataRequest
            msg = f'{MessageTypeBetweenNodes.newServerDataRequest.value}0#'
            temp_sock.send(msg.encode())

            # TODO receive newServerDataTransfer

            msg = MessageBetweenNodes()
            msg.recv(temp_sock)
            # TODO add all the the other nodes to list of nodes

            nodes_address_received = json.loads(msg.content)

            t = threading.Thread(target=self.handle_node, args=(temp_sock, node_address,))
            t.start()
            for node_address in nodes_address_received:
                ip = node_address[0]
                port = node_address[1]
                sock = socket.socket()
                sock.connect((ip, port))
                self.list_of_nodes.append((sock, node_address))
                t = threading.Thread(target=self.handle_node, args=(sock, node_address,))
                t.start()
            self.list_of_nodes.append((temp_sock, node_address))


        except ConnectionRefusedError or socket.timeout:
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

    def handle_new_server_data_request(self, content, sock: socket.socket,address):
        address_list = []
        for node in self.list_of_nodes:
            if address == node[1]:
                continue
            address = node[1]
            print(type(address))
            address_list.append(address)
        json_string = json.dumps(address_list)
        msg = MessageBetweenNodes(message_type=MessageTypeBetweenNodes.newServerDataTransfer, content=json_string)
        msg.send(sock)

    def handle_get_blocks(self, content, sock: socket.socket):
        pass

    def handle_new_block(self, content):
        pass

    def handle_node(self, node_socket: socket, address: tuple):
        node_socket.settimeout(SOCKET_RECEIVE_TIMEOUT)
        try:
            while True:
                try:
                    msg = MessageBetweenNodes()
                    msg.recv(node_socket)
                    self.lock.acquire()
                    if msg.message_type == MessageTypeBetweenNodes.newServerDataRequest:
                        self.handle_new_server_data_request(msg.content, node_socket,address)
                    elif msg.message_type == MessageTypeBetweenNodes.LogOff:
                        self.handle_log_off(msg.content)
                    elif msg.message_type == MessageTypeBetweenNodes.getBlocks:
                        self.handle_get_blocks(msg.content, node_socket)
                    elif msg.message_type == MessageTypeBetweenNodes.NewBlock:
                        self.handle_new_block(msg.content)
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
            print(e)
            # remove node from list of online nodes
            self.lock.acquire()
            self.list_of_nodes.remove((node_socket, address))
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
                self.list_of_nodes.append((node_socket, address))
                t = threading.Thread(target=self.handle_node, args=(node_socket, address,))
                t.start()
            except socket.timeout:
                pass
