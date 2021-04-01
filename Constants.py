import os
from pathlib import Path

# connection {
PORT_FOR_NODES = 89
PORT_FOR_CLIENTS = 233

MAX_NODES_CONNECTION = 50
MAX_CLIENTS_CONNECTION = 50

SOCKET_ACCEPT_TIMEOUT = 0.1
SOCKET_RECEIVE_TIMEOUT = 0.1
# }

# networking {
END_MSG = '$'
MSG_SEPARATOR = '~'
# }

# client{
SOCKET_CLIENT_RECEIVE_LONG_TIMEOUT = 2
SOCKET_CLIENT_RECEIVE_SHORT_TIMEOUT = 0.05
# }


# proof of work{
STARTING_REWARD_FOR_BLOCK = 2.0
MAX_NONCE = 2 ** 32  # 4 billion
PROOF_OF_WORK_CHECK_BLOCK_FREQUENCY = 10
CHANGE_REWARD_FOR_BLOCK_FREQUENCY = 500
# }

# encription {
KEY_BIT_LEN = 64
# }

# block {
MAX_LEN_OF_LIST_OF_NEW_USERS = 50
MAX_LEN_OF_LIST_OF_TRANSACTIONS = 20

# }


# GUI{
RECV_SCREEN_X_LEN = 28
RECANTS_SCREEN_X_LEN = 22


# }

# {
# ALLOWED_CHARACTERS = []
# ALLOWED_CHARACTERS.extend(string.ascii_lowercase)
# ALLOWED_CHARACTERS.extend(string.ascii_uppercase)
# ALLOWED_CHARACTERS.extend(string.digits)
# print(f"FORBIDDEN_CHARACTERS\n{ALLOWED_CHARACTERS}")
# }

def __file_name__(name: str, format='.png', path=str(str(Path.cwd() / 'res' / 'des'))) -> str:
    """
    A util function for helping in the path naming process.
    :param name: The name of the file.
    :param format: The format of the file. Default is PNG
    :param path: The abs path of the file. Default is under .../res/des/
    :return: The full abs path of the file.
    """

    f = name + format
    return os.path.join(path, f)


class Files:
    """
    A const class that contains all the files paths.
    """
    KV_DES_FILE = __file_name__("wallet_des", format='.kv', path=str(Path.cwd() / 'res'))
    DEF_FONT = __file_name__("Orion", format='.ttf', path=str(Path.cwd() / 'res'))

    MAIN_SCREEN = __file_name__("MAIN")
    CONNECT_SCREEN = __file_name__("connect")
    SIGN_UP_SCREEN = __file_name__("SignUp")
    WAITING_FOR_CONFIRMATION_SCREEN = __file_name__("WaitingForCon")
    USER_PAGE_SCREEN = __file_name__("UserPage")
    LOG_IN_SCREEN = __file_name__("LogIn")
    CREATE_FIRST_NODE_SCREEN = __file_name__("CreateFirstNode")
    USER_PAGE = __file_name__("UserPage")
    RECEIVE_SCREEN = __file_name__("Receive")
    RECEIVE_FULL_SCREEN = __file_name__("ReceiveFull")
    SEND_SCREEN = __file_name__("Send")

    BACK_BTN = __file_name__("BackBTN")
    CREATE_FIRST_NODE_BTN = __file_name__("CreateFirstNodeBTN")
    LOGIN_BTN = __file_name__("LoginBTN")
    SIGN_UP_BTN = __file_name__("SignUpBTN")
    SUBMIT_BTN = __file_name__("SubmitBTN")
    BIG_SEND_BTN = __file_name__("BigSendBTN")
    RECEIVE_BTN = __file_name__("ReceiveBTN")
    SEND_BTN = __file_name__("SendBTN")
    DECLINE_BTN = __file_name__("DeclineBTN")
