import socket
from datetime import datetime

from Constants import MSG_SEPARATOR, END_MSG
from utill.network.MessageType import MessageTypeBetweenNodes, MessageTypeBetweenNodeAndClient


class MessageBetweenNodes:
    def __init__(self, message_type: MessageTypeBetweenNodes = None, content: str = None):
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
        self.message_type = MessageTypeBetweenNodes(int(self.message_type))  # convert to enum

        print(f'####################\n', self.message_type.name, '\n', self.content, '\n####################')

    def send(self, sock: socket.socket):
        string_to_send = f'{self.message_type.value}{MSG_SEPARATOR}{self.content}{END_MSG}'
        print('sending',self.message_type.name,self.content,string_to_send)
        sock.send(string_to_send.encode())


class MessageBetweenNodeAndClient:
    def __init__(self, message_type: MessageTypeBetweenNodeAndClient = None, content: str = ''):
        self.message_type = message_type
        self.content = content

    # def recv(self, sock: socket.socket):
    #     msg = ''
    #     char = sock.recv(1).decode()
    #     if len(char) == 0:
    #         print("ConnectionError")
    #         raise ConnectionError
    #     msg += char
    #     while char != '#':
    #         if len(char) == 0:
    #             print("ConnectionError")
    #             raise ConnectionError
    #         char = sock.recv(1).decode()
    #         msg += char
    #     msg = msg[:-1]  # remove last item -> '#'
    #     print(msg)
    #     try:
    #         type, l = msg.split('~')
    #     except ValueError:
    #         raise ConnectionError
    #     self.message_type = MessageTypeBetweenNodeAndClient(int(type))
    #     length = int(l)
    #     if length == 0:
    #         return
    #     t = sock.gettimeout()
    #     sock.settimeout(10)
    #     self.content = sock.recv(length).decode()
    #     sock.settimeout(t)

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
        self.message_type = MessageTypeBetweenNodeAndClient(int(self.message_type))  # convert to enum
        print('rreerre')
        print(f'####################\n',self.message_type.name,'\n',self.content,'\n####################')

    def send(self, sock: socket.socket):
        string_to_send = f'{self.message_type.value}{MSG_SEPARATOR}{self.content}{END_MSG}'
        sock.send(string_to_send.encode())
