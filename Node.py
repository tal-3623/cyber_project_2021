import socket
import threading

from Constants import *
from Message import MessageBetweenNodes
from ServerDatabase import ServerDatabase


class Node:

    def __init__(self, username: str, pk: str):
        self.username = username
        self.server_database = ServerDatabase(username)
        self.pk = pk
        self.lock = threading.Lock()
        self.list_of_nodes = []
        self.list_of_clients = []
        self.list_of_transactions_to_make = []
        self.block_to_upload = None

        self.socket_for_nodes = socket.socket()
        self.socket_for_nodes.bind(('0.0.0.0', PORT_FOR_NODES))
        self.socket_for_nodes.listen(MAX_NODES_CONNECTION)
        self.socket_for_nodes.settimeout(SOCKET_ACCEPT_TIMEOUT)

        self.socket_for_clients = socket.socket()
        self.socket_for_clients.bind(('0.0.0.0', PORT_FOR_CLIENTS))
        self.socket_for_clients.listen(MAX_CLIENTS_CONNECTION)
        self.socket_for_clients.settimeout(SOCKET_ACCEPT_TIMEOUT)

    def initialize(self, node_address):
        temp_sock = socket.socket()
        temp_sock.connect((node_address[0], PORT_FOR_NODES))
        # TODO send newServerDataRequest
        # TODO add all the the other nodes to list _of nodes
        nodes_received = []
        self.list_of_nodes.extend(nodes_received)
        self.list_of_nodes.append((temp_sock, node_address)) 

    def handle_client(self, client_socket: socket, address):
        pass

    def handle_node(self, node_socket: socket, address):
        node_socket.settimeout(SOCKET_RECEIVE_TIMEOUT)
        try:

            while True:
                self.lock.acquire()
                if self.block_to_upload is not None:
                    pass  # TODO send block to node
                self.lock.release()

                try:
                    msg = MessageBetweenNodes()
                    msg.build_from_str(node_socket.recv().decode())
                    # TODO handle msg
                except socket.timeout:
                    pass
        except Exception as e:
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
                self.list_of_clients.append((node_socket, address))
                t = threading.Thread(target=self.handle_node, args=(node_socket, address,))
                t.start()
            except socket.timeout:
                pass
