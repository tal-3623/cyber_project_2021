import random

from Node2 import Node
from User import User


def l(names: list) -> list:
    a = []
    for name in names:
        a.append(User(name, str(random.randint(0, 100000))))
    return a


def main():
    node3 = Node(User("Main3", '3'), port_for_nodes=555, port_for_clients=333,
                 node_to_connect_through=("127.0.0.1", 989))
    a = l(['qq', "ww", "ee", "rr"])
    node3.acquire()
    node3.list_of_new_users_to_upload.extend(a)
    node3.release()
    node3.run()


if __name__ == '__main__':
    main()
