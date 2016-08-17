import random
import logging
import multiprocessing

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s [%(processName)s] - %(message)s')


def producer(q):
    while True:
        ret = random.randint(0, 100)
        logging.info('product {}'.format(ret))
        q.put(ret)


def consumer(q):
    while True:
        logging.info('consume {}'.format(q.get()))

q = multiprocessing.Queue()

p = multiprocessing.Process(target=producer, name='producer', args=(q, ))
c = multiprocessing.Process(target=consumer, name='consumer', args=(q, ))
p.start()
c.start()

p.join()
c.join()