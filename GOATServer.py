from client.WalletDatabase import WalletDatabase
from server.Node2 import Node
from utill.blockchain.User import User
from utill.encription.EncriptionKey import Key

# username = input('user ? ')
# password = input('password? ')
# port_for_nodes = int(input('port for nodes '))
# port_for_clients = int(input('port for clients '))
# is_first_node = input('is_first_node ').lower() == 't'
username = 'tal'
password = 'tal123'
port_for_nodes = 555
port_for_clients = 832
is_first_node = True
if not is_first_node:
    node_to_connect = (input("ip "), int(input('port ')))


def check_if_input_is_empty(*args):
    return '' in args


def check_username_validity(username: str):
    return username.isalnum()


def main():
    wallet_database = WalletDatabase('wallet')
    if is_first_node:
        if check_if_input_is_empty(username, password):
            print('fill out user and password')
            return
        elif not check_username_validity(username):
            print('username must be only letters and numbers')
            return

        if wallet_database.is_user_exist(username):
            if not wallet_database.check_if_password_valid(username, password):
                print('wrong password')
                return
            pk, private_key = wallet_database.get_keys(username, password)
        else:
            private_key = Key()
            pk = private_key.generate_public_key_and_private_key()
            wallet_database.add_new_user(username, password, private_key, pk)
        node = Node(User(username, pk), private_key, port_for_nodes=port_for_nodes, port_for_clients=port_for_clients)
        node.run()

    else:
        if wallet_database.is_user_exist(username):
            if not wallet_database.check_if_password_valid(username, password):
                print('wrong password')
                return
            pk, private_key = wallet_database.get_keys(username, password)
        else:
            private_key = Key()
            pk = private_key.generate_public_key_and_private_key()
            wallet_database.add_new_user(username, password, private_key, pk)
        pk, private_key = wallet_database.get_keys(username, password)
        node = Node(User(username, pk), private_key, port_for_nodes=port_for_nodes, port_for_clients=port_for_clients,
                    node_to_connect_through=node_to_connect)
        node.run()


if __name__ == '__main__':
    main()
