import socket

from MessageType import MessageTypeBetweenNodes


class MessageBetweenNodes:
    def __init__(self, message_type: MessageTypeBetweenNodes = None, content: str = None):
        self.message_type = message_type
        self.content = content

    def recv(self, sock: socket.socket):
        msg = ''
        char = sock.recv(1).decode()
        msg += char
        while char != '#':
            char = sock.recv(1).decode()
            msg += char
        msg = msg[:-1]  # remove last item -> '#'
        self.message_type = MessageTypeBetweenNodes(int(msg[0]))
        length = int(msg[1:])
        self.content = sock.recv(length)

    def send(self, sock: socket.socket):
        string_to_send = f'{self.message_type.value}{len(self.content)}#{self.content}'
        sock.send(string_to_send.encode())
