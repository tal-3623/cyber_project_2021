from Node import Node


def main():

    node3 = Node("bla", port_for_nodes=231, port_for_clients=23863, node_to_connect_through=("127.0.0.1", 989))
    node3.run()


if __name__ == '__main__':
    main()
