from Node2 import Node
from User import User


def l(names: list) -> list:
    a = []
    for i in range(len(names), len(names) * 2):
        a.append(User(names[i-len(names)], str(i + 3)))
    return a


def main():
    node = Node(User('Main1', '1'), port_for_nodes=989, port_for_clients=832)
    a = l(['aa', "bb", "cc", "dd"])
    node.acquire()
    node.list_of_new_users_to_upload.extend(a)
    node.release()
    node.run()


if __name__ == '__main__':
    main()
