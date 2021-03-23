from server.Node2 import Node
from utill.encription.EncriptionKey import Key
from utill.blockchain.Transaction import Transaction
from utill.blockchain.User import User


def l(names: list):
    a = []
    for i in range(len(names), len(names) * 2):
        private = Key()
        pub = private.generate_public_key_and_private_key()
        if names[i - len(names)] == 'qq':
            x = private
            y = pub
        a.append(User(names[i - len(names)], pub))

    print(f'qq key {x.as_str()}')
    return a, x, y


def main():
    key_private = Key()
    pub = key_private.generate_public_key_and_private_key()

    node = Node(User('Main3', pub), port_for_nodes=5432, port_for_clients=2452, node_to_connect_through=('127.0.0.1',989))
    a, x, y = l(['qq', "ee", "rr", "mm"])
    node.acquire()
    node.list_of_new_users_to_upload.extend(a)
    t = Transaction('Main3', 'qq', 1.7654, 'for test')
    sender_s = key_private.sign(t.data_as_str())
    rec_s = x.sign(t.data_as_str())
    t.sender_signature = sender_s
    t.receiver_signature = rec_s
    node.list_of_transactions_to_make.extend([t])
    node.release()
    node.run()


if __name__ == '__main__':
    main()
