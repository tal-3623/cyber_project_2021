import socket
import threading

from Constants import *
from Message import MessageBetweenNodes
from ServerDatabase import ServerDatabase


class Node:

    def __init__(self, username: str, pk: str, port_for_nodes: int, port_for_clients: int,
                 node_to_connect_through=None):

        self.username = username
        self.server_database = ServerDatabase(username)
        self.pk = pk
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

    def initialize(self, node_address):
        try:
            temp_sock = socket.socket()
            temp_sock.connect((node_address[0], node_address[1]))

            # TODO send newServerDataRequest
            # TODO add all the the other nodes to list _of nodes
            nodes_received = []

            self.list_of_nodes.extend(nodes_received)
            t = threading.Thread(target=self.handle_node, args=(temp_sock, node_address,))
            t.start()
            for node in self.list_of_nodes:
                node_socket = node[0]
                node_address = node[1]
                temp_sock = socket.socket()
                temp_sock.connect((node_address[0], node_address[1]))
                t = threading.Thread(target=self.handle_node, args=(node_socket, node_address,))
                t.start()
            self.list_of_nodes.append((temp_sock, node_address))

        except ConnectionRefusedError:
            print("the server to connect through is offline!")
            # TODO decise what to do when the  server to connect through is offline
            raise Exception("stop")

    def handle_client(self, client_socket: socket, address):
        pass

    def handle_node(self, node_socket: socket, address: tuple):
        node_socket.settimeout(SOCKET_RECEIVE_TIMEOUT)
        try:

            while True:
                self.lock.acquire()
                if self.block_to_upload is not None:
                    pass  # TODO send block to node
                self.lock.release()

                try:
                    msg = MessageBetweenNodes()
                    msg.build_from_str(node_socket.recv(1024).decode())
                    # TODO handle msg
                except socket.timeout:
                    pass
        except ConnectionError as e:
            print(e)
            # remove node from list of online nodes
            self.lock.acquire()
            self.list_of_nodes.remove((node_socket, address))
            self.lock.release()

    def run(self):
        while True:
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
