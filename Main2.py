from Node import Node


def main():

    node2 = Node("bla", port_for_nodes=4322, port_for_clients=2333, node_to_connect_through=("127.0.0.1", 989))

    node2.run()


if __name__ == '__main__':
    main()
