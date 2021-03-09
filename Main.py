from Node import Node
from User import User


def main():
    node = Node(User('Main1', '1'), port_for_nodes=989, port_for_clients=832)
    node.run()


if __name__ == '__main__':
    main()
