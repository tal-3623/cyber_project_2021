import json

from EncriptionKey import Key


class User:

    def __init__(self, username: str, pk: Key, balance: float = 0):
        self.username = username
        self.pk = pk
        self.balance = balance

    def as_str(self):
        list_of_components = [self.username, self.pk.as_str(), self.balance]
        return json.dumps(list_of_components)

    @staticmethod
    def create_from_str(string: str):
        l = json.loads(string)
        return User(l[0], Key.create_from_str(l[1]), int(l[2]))
