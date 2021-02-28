from Block import Block
from ServerDatabase import ServerDatabase

s = ServerDatabase('tal', True)
s.acquire()
s.print_data()
b1 = Block('tal', [], [], '')
s.release()

s.acquire()

s.release()

s.acquire()

s.release()

s.acquire()

s.release()

s.acquire()

s.release()

# import datetime
# print(datetime.datetime.now())
