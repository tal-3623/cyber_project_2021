import hashlib


class GeneralFunctions:
    @staticmethod
    def double_hash(data):
        """

        :return:the hash of the data after two sha 256 functions
        """
        return hashlib.sha256(hashlib.sha256(data).hexdigest().encode()).hexdigest()
