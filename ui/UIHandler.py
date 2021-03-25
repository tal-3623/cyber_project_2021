import json
import socket
from threading import Lock

from kivy.clock import Clock
from kivy.config import Config
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


class SignUpScreen(Screen):
    pass


class LogInScreen(Screen):
    pass


class WaitingForConfirmationScreen(Screen):
    pass


class UserPageScreen(Screen):
    pass


class CreateFirstNodeScreen(Screen):
    pass


'''
    Widgets & Utils
'''


class RecantsTransactions(ScrollView):
    def __init__(self, **kwargs):
        super(RecantsTransactions, self).__init__(**kwargs)

        self.bar_width = 30
        self.size_hint = (1, 0.81)
        self.scroll_type = ['bars']
        self.bar_inactive_color = (5, 20, 10, 0.5)
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.__init__grid()

    def __init__grid(self):
        self.grid = GridLayout()
        self.grid.size_hint_y = None
        self.grid.cols = 1
        self.grid.spacing = 0
        self.grid.padding = (0, -100)
        self.grid.size_hint_x = 1.0
        self.grid.row_default_height = '48dp'
        self.add_widget(self.grid)

    def add_transactions(self, list_of_transactions: list):
        tran: Transaction
        for tran in list_of_transactions:
            widg = Label(text=repr(tran))
            widg.size_hint_y = None
            widg.font_size = 36
            widg.padding = (0, 0)
            widg.height = 50
            widg.valign = 'middle'
            widg.halign = 'left'

            # increment grid height
            self.grid.height += widg.height
            self.grid.add_widget(widg)

    def clean(self):
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
        self.assets = Constants.Files
        self.kv_des = Builder.load_file(self.assets.KV_DES_FILE)
        self.wallet_database = WalletDatabase('wallet')
        self.lock = Lock()
        self.my_socket = socket.socket()
        self.my_socket.settimeout(Constants.SOCKET_CLIENT_RECEIVE_LONG_TIMEOUT)
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
            if self.root.current == "SignUpScreen":
                self.root.current = "MenuScreen"
                self.close_socket()
            if self.root.current == "LogInScreen":
                self.root.current = "MenuScreen"
                self.close_socket()
            if self.root.current == "WaitingForConfirmationScreen":
                self.root.current = "MenuScreen"
                self.close_socket()

    def close_socket(self):
        self.my_socket.close()
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.settimeout(Constants.SOCKET_CLIENT_RECEIVE_LONG_TIMEOUT)

    def log_in(self):
        print('hererererer')
        username = self.root.ids.LogInScreen.ids.username_wig.text
        password = self.root.ids.LogInScreen.ids.password_wig.text
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
                    self.root.current = "MenuScreen"
                    PopUp_Invalid_input('login failed')
                    self.current_user.clear()
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
                    self.my_socket.settimeout(0.5)
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
        print('acquire')
        self.lock.acquire()

    def release(self):
        self.lock.release()

    def process_transaction(self, transaction: Transaction):
        pass

    def recv_msg_from_server(self):
        self.acquire()
        if self.root.current in ["UserPageScreen"]:  # TODO add all needed screens
            try:
                msg = MessageBetweenNodeAndClient()
                msg.recv(self.my_socket)
                if msg.message_type == MessageTypeBetweenNodeAndClient.RECEIVE_ALL_TRANSACTIONS:
                    list_of_transactions = [Transaction.create_from_str(string) for string in json.loads(msg.content)]
                    for transaction in list_of_transactions:
                        self.process_transaction(transaction)
                elif msg.message_type == MessageTypeBetweenNodeAndClient.TRANSACTION_OFFERED:
                    pass
                elif msg.message_type == MessageTypeBetweenNodeAndClient.TRANSACTION_COMPLETED:
                    pass

            except socket.timeout:
                self.release()
                return
            except ConnectionError:
                print('server dissconected')  # TODO

        self.release()

    def create_first_node(self):
        username = self.root.ids.CreateFirstNodeScreen.ids.username_wig
        password = self.root.ids.CreateFirstNodeScreen.ids.password_wig
        port_for_nodes = self.root.ids.CreateFirstNodeScreen.ids.port_for_nodes_wig
        port_for_clients = self.root.ids.CreateFirstNodeScreen.ids.port_for_clients_wig

        self.root.ids.CreateFirstNodeScreen.ids.username_wig = ''
        self.root.ids.CreateFirstNodeScreen.ids.password_wig = ''
        self.root.ids.CreateFirstNodeScreen.ids.port_for_nodes_wig = ''
        self.root.ids.CreateFirstNodeScreen.ids.port_for_clients_wig = ' '


