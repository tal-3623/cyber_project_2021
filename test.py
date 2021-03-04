import hashlib

from Block import Block
from Constants import MAX_NONCE
from ServerDatabase import ServerDatabase
from User import User


def proof_of_work(block_as_str: str, difficulty_bits: int):
    target = 2 ** (256 - difficulty_bits)
    for nonce in range(MAX_NONCE):
        input_to_hash = block_as_str + str(nonce)
        hash_result = hashlib.sha256(input_to_hash.encode()).hexdigest()

        if int(hash_result, 16) < target:
            print(f"Success with nonce {nonce}")
            print(f"Hash is {hash_result}")
            return nonce

    return nonce


genesis_block = Block('genesis', [], [], '', '')
diff = 12


def create_new_block(username, LOT, LONW, LB: Block):
    b1 = Block(username, LOT, LONW, LB.current_block_hash)
    b1.proof_of_work = proof_of_work(LB.as_str(), diff)
    return b1


s = ServerDatabase('tal', True)

s.acquire()
s.print_data()
b = create_new_block('name1', [], [User('name1', 'fd4ab')], genesis_block)
s.add_block(b)
s.print_data()
s.release()

s.acquire()
s.print_data()
b = create_new_block('name2', [], [], b)
s.add_block(b)
s.print_data()
s.release()

s.acquire()
s.print_data()
b = create_new_block('name3', [], [], b)
s.add_block(b)
s.print_data()
s.release()

s.acquire()
s.print_data()
b = create_new_block('name4', [], [], b)
name4 = b
s.add_block(b)
s.print_data()
s.release()

s.acquire()
s.print_data()
b = create_new_block('name5', [], [], b)
s.add_block(b)
s.print_data()
s.release()

s.acquire()
s.print_data()
b = create_new_block('name6', [], [], b)
s.add_block(b)
s.print_data()
s.release()

s.acquire()
s.print_data()
b = create_new_block('name7', [], [], name4)
s.add_block(b)
s.print_data()
s.release()

s.acquire()
s.print_data()
b = create_new_block('name8', [], [], b)
s.add_block(b)
s.print_data()
s.release()

# import datetime
# print(datetime.datetime.now())
