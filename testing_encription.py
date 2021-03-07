import json
import math


def HexToByte(hexStr):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    # The list comprehension implementation is fractionally slower in this case
    #
    #    hexStr = ''.join( hexStr.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hexStr ), 2) ] )

    bytes = []

    hexStr = ''.join(hexStr.split(" "))

    for i in range(0, len(hexStr), 2):
        bytes.append(chr(int(hexStr[i:i + 2], 16)))

    return ''.join(bytes)


def ByteToHex(byteStr):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """

    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()

    return ''.join(["%02X " % ord(x) for x in byteStr]).strip()


# Function to find gcd
# of two numbers 
def euclid(m: int, n: int):
    # if n == 0:
    #     return m
    # else:
    #     r = m % n
    #     return euclid(n, r)
    return math.gcd(m, n)

    # Program to find


# Multiplicative inverse
def exteuclid(a, b):
    r1 = a
    r2 = b
    s1 = int(1)
    s2 = int(0)
    t1 = int(0)
    t2 = int(1)

    while r2 > 0:
        q = r1 // r2
        r = r1 - q * r2
        r1 = r2
        r2 = r
        s = s1 - q * s2
        s1 = s2
        s2 = s
        t = t1 - q * t2
        t1 = t2
        t2 = t

    if t1 < 0:
        t1 = t1 % a

    return (r1, t1)


def main():
    # Enter two large prime
    # numbers p and q
    p = 823
    q = 953
    n = p * q
    Pn = (p - 1) * (q - 1)

    # Generate encryption key
    # in range 1<e<Pn
    key = []

    for i in range(2, Pn):

        gcd = euclid(Pn, i)

        if gcd == 1:
            key.append(i)

        # Select an encryption key
    # from the above list
    e = key[1]

    # Obtain inverse of
    # encryption key in Z_Pn
    r, d = exteuclid(Pn, e)
    if r == 1:
        d = int(d)
        print("decryption key is: ", d)

    else:
        print("Multiplicative inverse for\
        the given encryption key does not \
            exist. Choose a different encrytion key ")

    # Enter the message to be sent
    M = int('tal is a goat'.encode().hex(), base=16)

    # Signature is created by Alice
    S = (M ** d) % n
    print(f's {S} m {M}')

    b = str(M) + str(S)
    l = [str(M), str(S)]
    string_to_send = json.dumps(l)
    b = string_to_send.encode()

    # send m and s
    # recv b

    M, S = json.loads(b.decode())
    M = int(M)
    S = int(S)

    print(f's {S} m {M}')


    # Alice sends M and S both to Bob
    # Bob generates message M1 using the
    # signature S, Alice's public key e
    # and product n.

    M1 = (S ** e) % n

    print(f'm {M} M1 {M1}')

    # If M = M1 only then Bob accepts
    # the message sent by Alice.

    if M == M1:
        print("As M = M1, Accept the\
    message sent by Alice")
    else:
        print("As M not equal to M1,\
    Do not accept the message \
            sent by Alice ")


main()

# m = 432
#
# if len(str(m)) % 2 != 0:
#     m *= 10
#
# h = hex(m)[2:]
#
# b = HexToByte(h)
#
# # send b
# # recv b
#
#
# new_h = ByteToHex(b).replace(' ', '').lower()
# print(f'h {h} new_h {new_h}')
#
# new_m = int(new_h, base=16)
#
# print(f'm is {m} new m {new_m}')
