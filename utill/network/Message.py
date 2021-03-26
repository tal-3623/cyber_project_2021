import socket

from utill.network.MessageType import MessageTypeBetweenNodes, MessageTypeBetweenNodeAndClient


class MessageBetweenNodes:
    def __init__(self, message_type: MessageTypeBetweenNodes = None, content: str = None):
        self.message_type = message_type
        self.content = content

    def recv(self, sock: socket.socket):
        msg = ''
        char = sock.recv(1).decode()
        if len(char) == 0:
            print("ConnectionError")
            raise ConnectionError
        msg += char
        while char != '#':
            if len(char) == 0:
                print("ConnectionError")
                raise ConnectionError
            char = sock.recv(1).decode()
            msg += char
        msg = msg[:-1]  # remove last item -> '#'
        self.message_type = MessageTypeBetweenNodes(int(msg[0]))
        length = int(msg[1:])
        self.content = sock.recv(length).decode()

    def send(self, sock: socket.socket):
        string_to_send = f'{self.message_type.value}{len(self.content)}#{self.content}'
        sock.send(string_to_send.encode())


class MessageBetweenNodeAndClient:
    def __init__(self, message_type: MessageTypeBetweenNodeAndClient = None, content: str = ''):
        self.message_type = message_type
        self.content = content

    def recv(self, sock: socket.socket):
        msg = ''
        char = sock.recv(1).decode()
        if len(char) == 0:
            print("ConnectionError")
            raise ConnectionError
        msg += char
        while char != '#':
            if len(char) == 0:
                print("ConnectionError")
                raise ConnectionError
            char = sock.recv(1).decode()
            msg += char
        msg = msg[:-1]  # remove last item -> '#'
        type, l = msg.split('~')
        self.message_type = MessageTypeBetweenNodeAndClient(int(type))
        length = int(l)
        self.content = sock.recv(length).decode()

    def send(self, sock: socket.socket):
        string_to_send = f'{self.message_type.value}~{len(self.content)}#{self.content}'
        sock.send(string_to_send.encode())
