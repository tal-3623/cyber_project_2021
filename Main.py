from Node import Node


def main():
    node = Node("tal", '1', port_for_nodes=989, port_for_clients=832)
    node.run()


if __name__ == '__main__':
    main()
