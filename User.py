import json


class User:

    def __init__(self, username: str, pk: str, balance: int = 0):
        self.username = username
        self.pk = pk
        self.balance = balance

    def as_str(self):
        list_of_components = [self.username, self.pk, self.balance]
        return json.dumps(list_of_components)

    @staticmethod
    def create_from_str(string: str):
        l = json.loads(string)
        return User(l[0], l[1], int(l[2]))
