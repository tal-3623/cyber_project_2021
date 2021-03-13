import random

from Node2 import Node
from Transaction import Transaction
from User import User


def l(names: list) -> list:
    a = []
    for name in names:
        a.append(User(name, str(random.randint(0, 10000))))
    return a


def main():
    node2 = Node(User("Main2", '2'), port_for_nodes=4322, port_for_clients=2333,
                 node_to_connect_through=("127.0.0.1", 989))
    a = l(['tal', "ofek", "moshe", "mamas"])
    node2.acquire()
    node2.list_of_new_users_to_upload.extend(a)
    node2.list_of_transactions_to_make.extend([Transaction('Main2','tal',333.9,'bummbele')])
    node2.release()
    node2.run()


if __name__ == '__main__':
    main()
