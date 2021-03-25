import json
import random
import time
from hashlib import sha256

from Constants import KEY_BIT_LEN
from utill.encription.Encription import coprime, modinv
from utill.encription.GeneratePrime import generate_prime


class Key:
    def __init__(self, key=None, n=None):
        self.__key = key
        self.__n = n

    def as_str(self):
        return json.dumps([self.__key, self.__n])

    @staticmethod
    def create_from_str(string: str):
        key, n = json.loads(string)
        return Key(key, n)

    def encrypt(self, msg: str):
        numberRepr = [ord(char) for char in msg]
        cipher = [pow(ord(char), self.__key, self.__n) for char in msg]

        # Return the array of bytes
        return cipher

    def decrypt(self, cipher):
        """

        :param cipher:
        :return: the decrypted cipher, if the key matches the cipher
        """

        numberRepr = [pow(char, self.__key, self.__n) for char in cipher]

        try:
            plain = [chr(num) for num in numberRepr]
        except OverflowError:
            print('OverflowError')
            return '', False  # aka the key could not decrypt probably cause he don't match


        # Return the array of bytes as a string
        return ''.join(plain), True

    def generate_public_key_and_private_key(self):
        """
        this func generates a private key and returns his public key
        :return:
        """
        p = generate_prime(KEY_BIT_LEN)
        while True:
            q = generate_prime(KEY_BIT_LEN)
            if p != q:
                break

        if p == q:
            raise ValueError('p and q cannot be equal')

        n = p * q

        # Phi is the totient of n
        phi = (p - 1) * (q - 1)

        # Choose an integer e such that e and phi(n) are coprime
        e = random.randrange(1, phi)

        # Use Euclid's Algorithm to verify that e and phi(n) are comprime
        g = coprime(e, phi)

        while g != 1:
            e = random.randrange(1, phi)
            g = coprime(e, phi)

        # Use Extended Euclid's Algorithm to generate the private key
        d = modinv(e, phi)

        # Return public and private keypair
        # Public key is (e, n) and private key is (d, n)
        self.__key = d
        self.__n = n
        public_key = Key(e, n)
        return public_key

    @staticmethod
    def hashFunction(message):
        hashed = sha256(message.encode("UTF-8")).hexdigest()
        return hashed

    def verify(self, signature: str, message: str):
        signature = json.loads(signature)
        signature, is_successful = self.decrypt(signature)
        if not is_successful:
            return False
        ourHashed = Key.hashFunction(message)
        if signature == ourHashed:
            print("Verification successful: ", )
            return True
        else:
            print("Verification failed")
            return False

    def sign(self, msg: str) -> str:
        """
        :param msg: the message you want to sign
        :return: the singature
        """
        hashed = self.hashFunction(msg)
        signature = self.encrypt(hashed)
        return json.dumps(signature)

    # TODO delete{
    def set(self, k, n):
        self.__key = k
        self.__n = n


def main():
    # p = int(input("Enter a prime number (17, 19, 23, etc): "))
    # q = int(input("Enter another prime number (Not one you entered above): "))
    t = time.time()

    print("Generating your public/private keypairs now . . .")
    private = Key()
    public = private.generate_public_key_and_private_key()
    print(time.time() - t)

    print("Your public key is ", public, " and your private key is ", private)
    message = input("Enter a message to encrypt with your private key: ")
    print("")

    print("Encrypting message with private key ", private, " . . .")
    signature = private.sign(message)
    print("Your encrypted hashed message is: ")

    print(signature)
    # print(encrypted_msg)

    print("")
    print("Decrypting message with public key ", public, " . . .")

    print("")
    print("Verification process . . .")
    public.verify(signature, message)


if __name__ == '__main__':
    main()
