import json
import socket
from threading import Lock

from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

import Constants
from client.CurrentUser import CurrentUser
from client.ParamsWaitingForConfirmation import ParamsWaitingForConfirmation
from client.WalletDatabase import WalletDatabase
from utill.blockchain.Transaction import Transaction
from utill.encription.EncriptionKey import Key
from utill.network.Message import MessageBetweenNodeAndClient
from utill.network.MessageType import MessageTypeBetweenNodeAndClient

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput

from ui.ComplexButton import ComplexButton

'''
    Screens
'''


class WindowManager(ScreenManager):
    pass


class MenuScreen(Screen):
    pass


class ConnectScreen(Screen):
    pass

    def clear_text(self):
        self.ids.ip_wig.text = ''
        self.ids.port_wig.text = ''


class SignUpScreen(Screen):
    pass

    def clear_text(self):
        self.ids.username_wig.text = ''
        self.ids.password_wig.text = ''


class LogInScreen(Screen):
    pass

    def clear_text(self):
        self.ids.username_wig.text = ''
        self.ids.password_wig.text = ''


class WaitingForConfirmationScreen(Screen):
    pass


class UserPageScreen(Screen):
    pass


class SendScreen(Screen):
    pass

    def clear_text(self):
        self.ids.receiver_username_wig.text = ''
        self.ids.amount_wig.text = ''
        self.ids.description_wig.text = ''


class ReceiveScreen(Screen):
    pass


class FullReceiveScreen(Screen):
    pass


# TODO: delate
class CreateFirstNodeScreen(Screen):
    pass


'''
    Widgets & Utils
'''


class TransactionLabel(ButtonBehavior, Label):
    def __init__(self, transaction: Transaction, **kwargs, ):
        super().__init__(**kwargs)
        print(f'type is {type(transaction)}')
        self.transaction = transaction
        self.opacity = 1

    # def on_press(self):
    #     self.opacity = self.opacity+0.5

    # def on_release(self):
    #     self.opacity = 0.2 if self.opacity == 1 else 1


def transform_into_multi_line(text: str, max_chars_in_line: int):
    list_of_words = text.split(' ')
    current_amount_of_chars = 0
    amount_of_lines = 1
    new_list = []
    for word in list_of_words:
        if len(word) + current_amount_of_chars + 1 > max_chars_in_line:
            word = '\n' + word
            current_amount_of_chars = 0
            new_list.append(word)
            amount_of_lines += 1
        else:
            current_amount_of_chars += len(word) + 1
            new_list.append(word)
    return ' '.join(new_list), amount_of_lines


class OfferedTransactions(ScrollView):
    def __init__(self, **kwargs):
        super(OfferedTransactions, self).__init__(**kwargs)

        self.bar_width = 30
        self.pos_hint = {'x': 0.25, 'y': 0.093}
        self.size_hint = (0.5, 0.6667)
        self.scroll_type = ['bars']
        self.bar_inactive_color = (5, 20, 10, 0.5)
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.__init__grid()

    def __init__grid(self):
        self.grid = GridLayout()
        self.grid.size_hint_y = None
        self.grid.cols = 1
        self.grid.spacing = 20
        self.grid.padding = (0, 0)
        self.grid.size_hint_x = 1.0
        self.grid.row_default_height = '24dp'
        self.add_widget(self.grid)
        self.list_of_trans = []

    def add_transactions(self, list_of_transactions: list, func_to_run_when_pressed):
        tran: Transaction

        for tran in self.list_of_trans:
            if tran not in list_of_transactions:  # aka tran has been deleted
                self.clean()

        for tran in list_of_transactions:
            print(f'tran type is {type(tran)} ,  {tran}')
            if tran in self.list_of_trans:
                print('contniue')
                continue
            text, amount_lines = transform_into_multi_line(str(tran), Constants.RECV_SCREEN_X_LEN)
            widg = TransactionLabel(tran, text=text)
            print(f'text is {widg.text}')
            # widg.size_hint_y = None
            widg.font_size = 30
            widg.padding = (0, 0)
            widg.height = amount_lines * (widg.font_size)
            widg.valign = 'middle'
            widg.halign = 'left'
            widg.on_press = func_to_run_when_pressed(tran)
            print(f'adding wig {widg.text}')
            # increment grid height
            self.grid.height += widg.height
            self.grid.add_widget(widg)
            self.list_of_trans.append(tran)

    def update_grid(self, list_of_transactions: list, func_to_run_when_pressed):
        self.add_transactions(list_of_transactions, func_to_run_when_pressed)

    def clean(self):
        print('clean')
        self.remove_widget(self.grid)
        self.__init__grid()
        self.list_of_trans = []


class RecantsTransactions(ScrollView):
    def __init__(self, **kwargs):
        super(RecantsTransactions, self).__init__(**kwargs)
        self.bar_width = 30
        self.pos_hint = {'x': 0.3255, 'y': 0.041667}
        self.size_hint = (0.3333, 0.3379)
        self.scroll_type = ['bars']
        self.bar_inactive_color = (5, 20, 10, 0.5)
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.__init__grid()

    def __init__grid(self):
        self.grid = GridLayout()
        self.grid.size_hint_y = None
        self.grid.cols = 1
        self.grid.spacing = 20
        self.grid.padding = (0, 0)
        self.grid.size_hint_x = 1.0
        self.grid.row_default_height = '24dp'
        self.add_widget(self.grid)
        self.list_of_trans = []

    def add_transactions(self, list_of_transactions: list):
        tran: Transaction

        for tran in list_of_transactions:
            if tran in self.list_of_trans:
                print('contniue')
                continue
            text, amount_lines = transform_into_multi_line(str(tran), Constants.RECANTS_SCREEN_X_LEN)
            widg = TransactionLabel(tran, text=text)
            print(f'text is {widg.text}')
            # widg.size_hint_y = None
            widg.font_size = 30
            widg.padding = (0, 0)
            widg.height = amount_lines * (widg.font_size)
            widg.valign = 'middle'
            widg.halign = 'left'
            print(f'adding wig {widg.text}')
            # increment grid height
            self.grid.height += widg.height
            self.grid.add_widget(widg)
            self.list_of_trans.append(tran)

    def update_grid(self, list_of_transactions: list):
        self.add_transactions(list_of_transactions)

    def clean(self):
        print('clean')
        self.remove_widget(self.grid)
        self.__init__grid()


class ImageButton(ComplexButton, Image):
    pass


class TextButton(ComplexButton, Label):
    pass


class BackButton(TextButton):
    pass


class TransTextInput(TextInput):
    def __init__(self, **kwargs):
        super(TransTextInput, self).__init__(**kwargs)


'''
    App
'''


def check_if_input_is_empty(*args):
    return '' in args


def PopUp_Invalid_input(text: str):
    pop = Popup(title='invalid input', content=Label(text=text), size_hint=(0.5, 0.5),
                pos_hint={'center_x': 0.5, 'center_y': 0.5})
    pop.open()
    del pop


def check_username_validity(username: str):
    return username.isalnum()


class WalletApp(App):
    def __init__(self, **kwargs):
        super(WalletApp, self).__init__(**kwargs)
        self.current_user = CurrentUser()
        self.current_transaction = None
        self.assets = Constants.Files
        self.kv_des = Builder.load_file(self.assets.KV_DES_FILE)
        self.wallet_database = WalletDatabase('wallet')
        self.lock = Lock()
        self.my_socket = socket.socket()
        self.my_socket.settimeout(Constants.SOCKET_CLIENT_RECEIVE_LONG_TIMEOUT)
        self.list_of_completed_transactions = []
        self.dict_of_repr_to_offered_transactions = {}
        Clock.schedule_interval(self.wait_for_confirmation, 1)

        self.connect_screen_from = None

    def connect(self):
        ip = self.root.ids.ConnectScreen.ids.ip_wig.text
        port = self.root.ids.ConnectScreen.ids.port_wig.text
        self.root.ids.ConnectScreen.ids.ip_wig.text = ""
        self.root.ids.ConnectScreen.ids.port_wig.text = ""
        if check_if_input_is_empty(ip, port) or not port.isnumeric():
            PopUp_Invalid_input('fill out correct ip and port')
            return
        self.my_socket.settimeout(0.1)
        try:
            self.my_socket.connect((ip, int(port)))
        except socket.timeout:
            self.close_socket()
            PopUp_Invalid_input(f'could not connect to server \nip : {ip}\nport : {port}')
            return
        if self.connect_screen_from == "sign up":
            self.root.current = "SignUpScreen"
        elif self.connect_screen_from == "log in":
            self.root.current = "LogInScreen"
        else:
            raise Exception('blaa')

    def build(self):
        self.title = "GOAT wallet"
        Window.size = (1920, 1080)
        Window.fullscreen = False
        return self.kv_des

    def wait_for_confirmation(self, *args):
        if self.root.current == "WaitingForConfirmationScreen":
            self.my_socket.settimeout(0.1)
            username = self.params_for_wait_for_confirmation.username
            password = self.params_for_wait_for_confirmation.password
            private_key = self.params_for_wait_for_confirmation.key_private
            public_key = self.params_for_wait_for_confirmation.pk
            try:
                msg = MessageBetweenNodeAndClient()
                msg.recv(self.my_socket)
                print(f'{msg.message_type.name}, {msg.content}')
                if msg.message_type == MessageTypeBetweenNodeAndClient.SIGN_UP_CONFIRMED:
                    # after the user has been processed{
                    pass  # TODO: add the new user to the db
                    print(f'adding to db{username, password, private_key, public_key}')
                    self.wallet_database.add_new_user(username, password, private_key, public_key)
                    # TODO: log into into the user
                    # }
                    self.pressed_back()
                elif msg.message_type == MessageTypeBetweenNodeAndClient.SIGN_UP_FAILED:
                    PopUp_Invalid_input('SIGN_UP_FAILED')
                    self.pressed_back()

            except socket.timeout:
                print('paass')
                pass

            except ConnectionError:
                PopUp_Invalid_input('SIGN_UP_FAILED')
                self.pressed_back()

    def pressed_back(self):
        """
        this func called when user bressed the back button
        this func will go back to the last screen the user viewed
        :return:
        """
        if self.root.current is not None:
            if self.root.current == "ConnectScreen":
                self.root.current = "MenuScreen"
                self.close_socket()
                self.root.ids.ConnectScreen.clear_text()
            elif self.root.current == "SignUpScreen":
                self.root.current = "MenuScreen"
                self.close_socket()
                self.root.ids.SignUpScreen.clear_text()
            elif self.root.current == "LogInScreen":
                self.root.current = "MenuScreen"
                self.close_socket()
                self.root.ids.LogInScreen.clear_text()
            elif self.root.current == "WaitingForConfirmationScreen":
                self.root.current = "MenuScreen"
                self.close_socket()
            elif self.root.current == "UserPageScreen":
                self.root.current = "MenuScreen"
                self.close_socket()
            elif self.root.current in ["ReceiveScreen", "FullReceiveScreen", "SendScreen"]:
                self.root.current = "UserPageScreen"
                self.root.ids.SendScreen.clear_text()

    def back_to_menu(self):
        self.root.current = "MenuScreen"
        self.close_socket()

    def close_socket(self):
        self.my_socket.close()
        print('close')
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.settimeout(Constants.SOCKET_CLIENT_RECEIVE_LONG_TIMEOUT)

    def log_in(self):
        print('hererererer')
        username = self.root.ids.LogInScreen.ids.username_wig.text
        password = self.root.ids.LogInScreen.ids.password_wig.text
        # username = 'g'
        # password = '1'
        self.root.ids.SignUpScreen.ids.username_wig.text = ""
        self.root.ids.SignUpScreen.ids.password_wig.text = ""
        if check_if_input_is_empty(username, password):
            PopUp_Invalid_input('fill out user and password')
        elif not check_username_validity(username):
            PopUp_Invalid_input('username must be only letters and numbers')
        elif not self.wallet_database.is_user_exist(username):
            PopUp_Invalid_input(f'no user named {username}')
        elif not self.wallet_database.check_if_password_valid(username, password):
            PopUp_Invalid_input(f'wrong password')
        else:  # password and user correct
            print('password and user correct')
            current_username = username
            current_password = password
            current_pk, current_private_key = self.wallet_database.get_keys(username, password)
            self.current_user.set(current_username, current_password, current_private_key,
                                  current_pk)
            #  Send log in server with the user{
            try:
                self.my_socket.settimeout(7)

                msg = MessageBetweenNodeAndClient(MessageTypeBetweenNodeAndClient.LOG_IN_REQUEST, username)
                msg.send(self.my_socket)

                msg = MessageBetweenNodeAndClient()
                print('reciving msg')
                msg.recv(self.my_socket)
                print(f'msg is {msg.message_type}, {msg.content}')

                if msg.message_type == MessageTypeBetweenNodeAndClient.LOG_IN_FAILED:
                    PopUp_Invalid_input('login failed')
                    self.current_user.clear()
                    self.pressed_back()
                    return
                elif msg.message_type != MessageTypeBetweenNodeAndClient.LOG_IN_RAND:
                    raise Exception('unxpected msg')

                print(f'bla {self.current_user.private_key}')
                signature = self.current_user.private_key.sign(msg.content)

                msg = MessageBetweenNodeAndClient(MessageTypeBetweenNodeAndClient.LOG_IN_RAND_ANSWER, signature)
                msg.send(self.my_socket)

                msg = MessageBetweenNodeAndClient()
                print('reciving')
                msg.recv(self.my_socket)
                print(f'msg is {msg.message_type}, {msg.content}')

                if msg.message_type == MessageTypeBetweenNodeAndClient.LOG_IN_ACCEPTED:
                    self.root.current = "UserPageScreen"
                    self.root.ids.UserPageScreen.ids.username_label.text = self.current_user.username
                    # send to server GET_ALL_TRANSACTIONS{
                    msg_to_send = MessageBetweenNodeAndClient(MessageTypeBetweenNodeAndClient.GET_ALL_TRANSACTIONS)
                    msg_to_send.send(self.my_socket)
                    self.my_socket.settimeout(Constants.SOCKET_CLIENT_RECEIVE_SHORT_TIMEOUT)
                    Clock.schedule_interval(self.recv_msg_from_server, 1)
                    # }
                    print(repr(self.current_user))
                elif msg.message_type == MessageTypeBetweenNodeAndClient.LOG_IN_FAILED:
                    PopUp_Invalid_input('login failed')
                    self.pressed_back()
                else:
                    raise Exception('nfds')
            except ConnectionError:
                PopUp_Invalid_input('server  off')
                self.pressed_back()
            # }

    def sign_up(self):
        username = self.root.ids.SignUpScreen.ids.username_wig.text
        password = self.root.ids.SignUpScreen.ids.password_wig.text
        print('usernmae', username, 'pass', password)
        self.root.ids.SignUpScreen.ids.username_wig.text = ""
        self.root.ids.SignUpScreen.ids.password_wig.text = ""
        if check_if_input_is_empty(username, password):
            PopUp_Invalid_input('fill out user and password')
        elif not check_username_validity(username):
            PopUp_Invalid_input('username must be only letters and numbers')
        else:
            while True:
                key_private = Key()
                pk = key_private.generate_public_key_and_private_key()

                # send sign up msg{
                list_of_data = [username, pk.as_str()]
                content = json.dumps(list_of_data)
                msg = MessageBetweenNodeAndClient(MessageTypeBetweenNodeAndClient.SIGN_UP, content)
                try:
                    self.my_socket.settimeout(2)
                    print(f'sending {msg.message_type.name}, {msg.content}')
                    msg.send(self.my_socket)

                    msg = MessageBetweenNodeAndClient()
                    msg.recv(self.my_socket)
                    print(f'recv {msg.message_type.name}, {msg.content}')
                except ConnectionError as e:
                    PopUp_Invalid_input("server went offline")
                    self.pressed_back()
                    return

                    # }

                is_user_name_taken = bool(int(msg.content[0]))
                is_pk_taken = bool(int(msg.content[1]))
                if is_user_name_taken:
                    PopUp_Invalid_input('username is taken')
                    return
                elif is_pk_taken:
                    continue
                else:
                    break

            print('waiting for conformation')

            self.root.current = "WaitingForConfirmationScreen"
            # TODO: wait to get conformation from server that the user has been processed
            # TODO: switch to a screen that says waiting for conformation

            self.params_for_wait_for_confirmation = ParamsWaitingForConfirmation(username, password, key_private, pk)

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()

    def update_balance(self, transaction=None, amount: float = None):
        """
        called only when the transaction is valid
        :param amount:
        :param transaction:
        :return:
        """

        print(f'balance before {self.current_user.balance}')
        if amount is not None:
            self.current_user.balance += amount
        elif self.current_user.username == transaction.sender_username:
            self.current_user.balance -= transaction.amount
        elif self.current_user.username == transaction.receiver_username:
            self.current_user.balance += transaction.amount
        else:
            raise Exception('im not the sender nor the receiver')
        # update gui {
        self.root.ids.UserPageScreen.ids.balance_label.text = str(round(self.current_user.balance, 5))
        # }
        print(f'balance after {self.current_user.balance}')

    def process_transaction(self, transaction: Transaction, type: MessageTypeBetweenNodeAndClient):
        print(
            f'in process tran {transaction.sender_username} to {transaction.receiver_username} amount {transaction.amount}')

        if type == MessageTypeBetweenNodeAndClient.TRANSACTION_COMPLETED:
            self.update_balance(transaction=transaction)
            self.list_of_completed_transactions.append(transaction)
            if transaction.__str__() in self.dict_of_repr_to_offered_transactions.keys():
                print('removing ->', self.dict_of_repr_to_offered_transactions.pop(transaction.__str__()))
            self.root.ids.UserPageScreen.ids.RecantsTransactions.update_grid(self.list_of_completed_transactions)
            self.root.ids.ReceiveScreen.ids.OfferedTransactions.update_grid(
                self.dict_of_repr_to_offered_transactions.values(), self.move_to_receive_full_screen)
        elif type == MessageTypeBetweenNodeAndClient.TRANSACTION_OFFERED:
            if transaction.as_str() in self.wallet_database.get_list_of_declined_transactions(
                    self.current_user.username):
                return
            self.dict_of_repr_to_offered_transactions[transaction.__str__()] = transaction
            self.root.ids.ReceiveScreen.ids.OfferedTransactions.update_grid(
                self.dict_of_repr_to_offered_transactions.values(), self.move_to_receive_full_screen)
        else:
            raise Exception(f'unxepect msg {type.name}')

    def recv_msg_from_server(self, *args):
        self.acquire()
        if self.root.current in ["UserPageScreen", "SendScreen", "FullReceiveScreen",
                                 "ReceiveScreen"]:  # TODO add all needed screens
            try:
                msg = MessageBetweenNodeAndClient()
                msg.recv(self.my_socket)
                print(f'received {msg.message_type}', msg.content)
                if msg.message_type == MessageTypeBetweenNodeAndClient.RECEIVE_ALL_TRANSACTIONS:
                    print('in RECEIVE_ALL_TRANSACTIONS')
                    list_of_transactions, money_from_uploading_blocks = json.loads(msg.content)
                    list_of_transactions = [
                        (Transaction.create_from_str(tup[0]), MessageTypeBetweenNodeAndClient(int(tup[1]))) for tup in
                        list_of_transactions]
                    for tup in list_of_transactions:
                        self.process_transaction(tup[0], tup[1])  # (transaction,msg_type)
                    self.update_balance(amount=float(money_from_uploading_blocks))
                elif msg.message_type in [MessageTypeBetweenNodeAndClient.TRANSACTION_OFFERED,
                                          MessageTypeBetweenNodeAndClient.TRANSACTION_COMPLETED]:
                    tran = Transaction.create_from_str(msg.content)
                    self.process_transaction(tran, msg.message_type)
                elif msg.message_type == MessageTypeBetweenNodeAndClient.BLOCK_UPLOADED:
                    amount = float(msg.content)
                    self.update_balance(amount=amount)



            except socket.timeout:
                self.release()
                return
            except ConnectionError:
                print('server dissconected')  # TODO
                self.root.current = "MenuScreen"
                self.close_socket()
                self.current_user.clear()

        self.release()

    def send_coins(self):
        """
        called when user pressed send in the send coins screen
        :return:

        """
        receiver_username = self.root.ids.SendScreen.ids.receiver_username_wig.text
        amount = self.root.ids.SendScreen.ids.amount_wig.text
        description = self.root.ids.SendScreen.ids.description_wig.text

        self.root.ids.SendScreen.ids.receiver_username_wig.text = ''
        self.root.ids.SendScreen.ids.amount_wig.text = ''
        self.root.ids.SendScreen.ids.description_wig.text = ''

        if check_if_input_is_empty(receiver_username, amount):
            PopUp_Invalid_input('fiil out username and amount ')
            return
        try:
            amount = float(amount)
        except ValueError:
            PopUp_Invalid_input('amount should be a a valid number')
            return
        transaction = Transaction(self.current_user.username, receiver_username, amount, description)
        signature = self.current_user.private_key.sign(transaction.data_as_str())
        transaction.sender_signature = signature

        try:
            msg = MessageBetweenNodeAndClient(MessageTypeBetweenNodeAndClient.TRANSACTION_OFFERED, transaction.as_str())
            print(f'sending {msg.message_type} , {msg.content}')
            msg.send(self.my_socket)
        except ConnectionError:
            self.back_to_menu()
            PopUp_Invalid_input('server dissconnected')
            return
        self.root.current = "UserPageScreen"

    def receive_coins(self):

        # update gui{
        self.dict_of_repr_to_offered_transactions.pop(self.current_transaction.__str__())
        self.root.ids.ReceiveScreen.ids.OfferedTransactions.update_grid(
            self.dict_of_repr_to_offered_transactions.values(), self.move_to_receive_full_screen)
        # }
        my_signature = self.current_user.private_key.sign(self.current_transaction.data_as_str())
        self.current_transaction.receiver_signature = my_signature

        # send transaction with signature to server{
        msg_to_send = MessageBetweenNodeAndClient(MessageTypeBetweenNodeAndClient.TRANSACTION_COMPLETED,
                                                  self.current_transaction.as_str())
        try:
            print(f'sending {msg_to_send.message_type}', msg_to_send.content)
            msg_to_send.send(self.my_socket)
            self.pressed_back()
        except ConnectionError:
            self.back_to_menu()
        # }

    def decline(self):
        print(self.dict_of_repr_to_offered_transactions)
        self.wallet_database.add_declined_transaction(self.current_user.username, self.current_transaction)
        self.dict_of_repr_to_offered_transactions.pop(self.current_transaction.__str__())
        self.root.ids.ReceiveScreen.ids.OfferedTransactions.update_grid(
            self.dict_of_repr_to_offered_transactions.values(), self.move_to_receive_full_screen)
        self.pressed_back()

    def move_to_receive_full_screen(self, transaction):

        def inner():
            self.root.current = "FullReceiveScreen"
            self.current_transaction = transaction

            self.root.ids.FullReceiveScreen.ids.from_label.text = transaction.sender_username
            self.root.ids.FullReceiveScreen.ids.amount_label.text = str(transaction.amount)
            self.root.ids.FullReceiveScreen.ids.description_label.text = transaction.description

        return inner
