import mysql.connector


class SingletonGovt:
    __instance__ = None

    def __init__(self):
        """ Constructor.
        """

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not SingletonGovt.__instance__:
            SingletonGovt()
        return SingletonGovt.__instance__


class ServerDatabase:
    __instance__ = None

    @staticmethod
    def get_instance(username: str = None, password: str = None):
        """ Static method to fetch the current instance.
        """
        if ServerDatabase.__instance__ is None:
            ServerDatabase(username, password)
        return ServerDatabase.__instance__

    def __init__(self, username: str, password: str):
        """
        :param username: username of the database
        :param password: password of the database
        """
        if ServerDatabase.__instance__ is None:
            ServerDatabase.__instance__ = self
        else:
            raise Exception("You cannot create another ServerDatabase class because it is a singleton class")

        self.username = username
        self.password = password
        self.connect()

    def connect(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user=self.username,
            password=self.password
        )
        self.cursor = mydb.cursor()

    def create_db(self):
        pass
