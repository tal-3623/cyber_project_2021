import json
import socket

from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.popup import Popup

import Constants
from client.ParamsWaitingForConfirmation import ParamsWaitingForConfirmation
from client.WalletDatabase import WalletDatabase
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


class WaitingForConfirmationScreen(Screen):
    pass


class UserPageScreen(Screen):
    pass


'''
    Widgets & Utils
'''


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
    Popup(title='invalid input', content=Label(text=text), size_hint=(0.5, 0.5),
          pos_hint={'center_x': 0.5, 'center_y': 0.5}).open()


def check_username_validity(username: str):
    return username.isalnum()
    # for char in username:
    #     if char not in Constants.ALLOWED_CHARACTERS:
    #         return False
    # return True


class WalletApp(App):
    def __init__(self, **kwargs):
        super(WalletApp, self).__init__(**kwargs)
        self.assets = Constants.Files
        self.kv_des = Builder.load_file(self.assets.KV_DES_FILE)
        self.wallet_database = WalletDatabase('wallet')
        self.my_socket = socket.socket()
        self.my_socket.settimeout(Constants.SOCKET_CLIENT_RECEIVE_TIMEOUT)
        Clock.schedule_interval(self.wait_for_confirmation,1)

        self.connect_screen_from = None

    def connect(self):
        ip = self.root.ids.ConnectScreen.ids.ip_wig.text
        port = self.root.ids.ConnectScreen.ids.port_wig.text
        self.root.ids.ConnectScreen.ids.ip_wig.text = ""
        self.root.ids.ConnectScreen.ids.port_wig.text = ""
        print("ip", ip, "port", port)
        print((ip, port))
        print(self.connect_screen_from)
        if check_if_input_is_empty(ip, port) or not port.isnumeric():
            PopUp_Invalid_input('fill out correct ip and port')
            return
        try:
            self.my_socket.connect((ip, int(port)))
        except ConnectionError or Exception :
            print("server is offline")
            PopUp_Invalid_input('could not connect to server')
            return
        if self.connect_screen_from == "sign up":
            self.root.current = "SignUpScreen"
        elif self.connect_screen_from == "log in":
            pass  # TODO
        else:
            raise Exception('blaa')

    def build(self):
        self.title = "GOAT wallet"
        Window.size = (1920, 1080)
        Window.fullscreen = False
        return self.kv_des

    def wait_for_confirmation(self,*args):
        if self.root.current == "WaitingForConfirmationScreen":
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
                    self.root.current = "UserPageScreen"
                elif msg.message_type == MessageTypeBetweenNodeAndClient.SIGN_UP_FAILED:
                    pass  # TODO

            except socket.timeout:
                print('paass')
                pass

    def pressed_back(self):
        """
        this func called when user bressed the back button
        this func will go back to the last screen the user viewed
        :return:
        """
        if self.root.current is not None:
            if self.root.current == "ConnectScreen":
                self.root.current = "MenuScreen"
            if self.root.current == "SignUpScreen":
                self.root.current = "MenuScreen"
                # TODO: disconnect socket

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
                    print(f'sending {msg.message_type.name}, {msg.content}')
                    msg.send(self.my_socket)

                    msg = MessageBetweenNodeAndClient()

                    msg.recv(self.my_socket)
                    print(f'recv {msg.message_type.name}, {msg.content}')

                except Exception as e:
                    raise e  # TODO: handle server dissconect
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
