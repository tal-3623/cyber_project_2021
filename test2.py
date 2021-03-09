import hashlib

from Block import Block
from Constants import MAX_NONCE
from ServerDatabase import ServerDatabase
from Transaction import Transaction
from User import User


def proof_of_work(block_as_str: str, difficulty_bits: int):
    target = 2 ** (256 - difficulty_bits)
    for nonce in range(MAX_NONCE):
        input_to_hash = block_as_str + str(nonce)
        hash_result = hashlib.sha256(input_to_hash.encode()).hexdigest()

        if int(hash_result, 16) < target:
            print(f'\nhash result {hash_result}\n input to hash {input_to_hash}\n')
            return nonce

    Exception('did not found')


genesis_block = Block('genesis', [], [], '', '')
diff = 15


def create_new_block(username, LOT, LONW, LB: Block):
    b1 = Block(username, LOT, LONW, LB.current_block_hash)
    b1.proof_of_work = proof_of_work(LB.as_str(), diff)
    return b1


s = ServerDatabase('tal', False)
s.blockchain_table.cursor.execute(f'''Select MAX(ID) From Blockchain''')
max_id_list = s.blockchain_table.cursor.fetchall()
if len(max_id_list) != 1:
    raise Exception("duplicate max id")
max_id = max_id_list[0][0]
s.blockchain_table.cursor.execute(f'''SELECT * FROM Blockchain WHERE ID = {max_id};''')
a = s.blockchain_table.cursor.fetchall()
last_block = Block.create_block_from_tuple(a[0])

s.acquire()
b = create_new_block('name6', [Transaction('Ofek', 'name1', 1.5, '')], [User('name6', '1236')], last_block)

t = b
# print(s.add_block(b))
s.print_data()
s.release()

s.acquire()
b = create_new_block('name7', [], [User('name7', '127')], b)
print(s.add_block(b))
s.print_data()
s.release()



s.acquire()
b = create_new_block('name8', [], [User('name8', '1238')], b)
s.add_block(b)
s.print_data()
s.release()

s.acquire()
b = create_new_block('name9', [], [User('name9', '129')], b)
s.add_block(b)
s.print_data()

print(s.add_block(t))

s.print_data()

s.release()


s.close()
















