import logging
import random
import queue
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s [%(threadName)s] - %(message)s')
event = threading.Event()


def info(x):
    while True:
        logging.info('info({}) function called'.format(x))
        event.wait(1)


def producer(q):
    while True:
        ret = random.randint(0, 100)
        logging.info('product {}'.format(ret))
        q.put(ret)


def consumer(q):
    while True:
        logging.info('consume {}'.format(q.get()))

# thread_1 = threading.Thread(target=info, name='thread-info-1', args=(1, ))
# thread_1.start()
#
# thread_2 = threading.Thread(target=info, name='thread-info-2', args=(2, ))
# thread_2.start()

q = queue.Queue()
p = threading.Thread(target=producer, name='producer', args=(q, ))
c = threading.Thread(target=consumer, name='counsumer', args=(q, ))

p.start()
c.start()