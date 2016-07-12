import os
import uuid
import socket

s = socket.socket()
s.connect(('127.0.0.1', 1234))
task_id = uuid.uuid4().hex
print(task_id)
s.send(task_id.encode())
s.send(b'\n')
hostname = os.uname().nodename
print(hostname)
s.send(hostname.encode())
s.send(b'\n')
s.send(b'1\n')
s.send(b'\n')

s.send(b'abcd')
s.close()