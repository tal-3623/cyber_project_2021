import socket

from Constants import MSG_SEPARATOR, END_MSG
from utill.network.MessageType import MessageType


class MessageBetweenNodes:
    def __init__(self, message_type: MessageType = None, content: str = None):
        self.message_type = message_type
        self.content = content

    def recv(self, sock: socket.socket):
        msg = ''
        while True:
            char = sock.recv(1).decode()
            if len(char) == 0:
                print("ConnectionError")
                raise ConnectionError
            elif char == END_MSG:
                break
            else:
                msg += char
        self.message_type, self.content = msg.split(MSG_SEPARATOR)
        self.message_type = MessageType(int(self.message_type))  # convert to enum


    def send(self, sock: socket.socket):
        string_to_send = f'{self.message_type.value}{MSG_SEPARATOR}{self.content}{END_MSG}'
        sock.send(string_to_send.encode())


class MessageBetweenNodeAndClient:
    def __init__(self, message_type: MessageType = None, content: str = ''):
        self.message_type = message_type
        self.content = content



    def recv(self, sock: socket.socket):
        msg = ''
        while True:
            char = sock.recv(1).decode()
            if len(char) == 0:
                print("ConnectionError")
                raise ConnectionError
            elif char == END_MSG:
                break
            else:
                msg += char
        self.message_type, self.content = msg.split(MSG_SEPARATOR)
        self.message_type = MessageType(int(self.message_type))  # convert to enum


    def send(self, sock: socket.socket):
        string_to_send = f'{self.message_type.value}{MSG_SEPARATOR}{self.content}{END_MSG}'
        sock.send(string_to_send.encode())
