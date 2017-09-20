# -*- coding:utf-8 -*-

import threading
import os
import time
import psutil
import logging

logging.basicConfig(format="%(threadName)s:%(message)s%%(thread)d")


def not_over(name):
    while True:
        time.sleep(5)
        print("======= not over", name)


def will_over(name):
    time.sleep(5)
    print('====== will over', name)

for i in range(3):
    t = threading.Thread(target=will_over, args=('sam',), name=str(i)+'-sam')
    # t.setDaemon(True)   # 不会等待线程运行完成，主线程直接结束
    t.start()
    print(t.name)
    logging.error('threading......')
    # t.join()
print("thread is over")

print(threading.current_thread().name, threading.current_thread().ident, os.getpid())
logging.error('process.....{}'.format(threading.current_thread()))
print(os.getppid(), os.getpid(), os.getuid())

# find thread id
import time
# get thread id

import ctypes

# libc = ctypes.cdll.LoadLibrary('libc.so.6')
SYS_gettid = 186


def getThreadId():
    return libc.syscall(SYS_gettid)


def find_thread(j):
    print('find thread .......{}'.format(j))
    logging.error('thread id how much is')
    threading._sleep(34)

for i in range(9):
    u = threading.Thread(target=find_thread, args=(i,), name=str(i)+'-jack')
    u.start()
    # u.join()
    tid = threading.local()
    print('tid {}'.format(tid))
    # logging.error(getThreadId())
time.sleep(300)
