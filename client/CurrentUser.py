from utill.encription.EncriptionKey import Key


class CurrentUser:

    def __init__(self):
        self.username = ''
        self.password = ''
        self.private_key = None
        self.public_key = None
        self.balance = 0

    def set(self, username: str, password: str, private_key: Key, public_key: Key):
        self.username = username
        self.password = password
        self.private_key = private_key
        self.public_key = public_key

    def clear(self):
        self.username = ''
        self.password = ''
        self.private_key = None
        self.public_key = None
        self.balance = 0

    def __repr__(self):
        return f'username {self.username}\npassword {self.password}'
