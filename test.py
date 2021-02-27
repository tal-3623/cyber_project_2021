import hashlib

from ServerDatabase import ServerDatabase

s = ServerDatabase('tal')
s.acquire()
parent_id = 3
l = 5
se = 98
UploaderUsername = 'go'.encode().decode()
LBH = int('LBH'.encode().hex(), base=16)
CBH = int('CBH'.encode().hex(), base=16)
POW = int(hashlib.sha256('POW'.encode()).hexdigest(), base=16)
Time = '11300'
sec = 1



s.blockchain_table.cursor.execute(f'''SELECT *  FROM Blockchain  ''')

s.blockchain_table.memory_cursor.execute(f'''SELECT *  FROM Blockchain  ''')

print(s.blockchain_table.cursor.fetchall())
print(s.blockchain_table.memory_cursor.fetchall())

s.release()

# import datetime
# print(datetime.datetime.now())
