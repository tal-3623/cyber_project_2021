from EncriptionKey import Key
from Node2 import Node
from Transaction import Transaction
from User import User


def l(names: list):
    a = []
    for i in range(len(names), len(names) * 2):
        private = Key()
        pub = private.generate_public_key_and_private_key()
        if names[i - len(names)] == 'aa':
            x = private
            y = pub
        a.append(User(names[i - len(names)], pub))

    print(f'aa key {x.as_str()}')
    return a, x, y


def main():
    key_private = Key()
    pub = key_private.generate_public_key_and_private_key()

    node = Node(User('Main1', pub), port_for_nodes=989, port_for_clients=832)
    a, x, y = l(['aa', "bb", "cc", "dd"])
    node.acquire()
    node.list_of_new_users_to_upload.extend(a)
    t = Transaction('Main1', 'aa', 0.5, 'for test')
    sender_s = key_private.sign(t.data_as_str())
    rec_s = x.sign(t.data_as_str())
    t.sender_signature = sender_s
    t.receiver_signature = rec_s
    node.list_of_transactions_to_make.extend([t])
    node.release()
    node.run()


if __name__ == '__main__':
    main()
