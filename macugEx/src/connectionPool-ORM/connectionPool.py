# -*- coding: utf-8 -*-
"""
简单MySQL连接池实现
"""
import pymysql
import queue
from contextlib import contextmanager
from pymysql.cursors import DictCursor


class ConnectionPool:
    def __init__(self, **kwargs):
        self.size = kwargs.pop('size', 10)
        self.idle = kwargs.pop('idle', 3)
        self.kwargs = kwargs
        self.length = 0
        self.connections = queue.Queue(maxsize=self.idle)

    def _connect(self):
        if not self.connections.full():
            conn = pymysql.connect(**self.kwargs)
            self.connections.put(conn)
            self.length += 1
        else:
            raise RuntimeError('lot of connections')

    def _close(self, conn):
        conn.close()
        self.length -= 1

    def get(self, timeout=None):
        if self.connections.empty() and self.length < self.size:
            self._connect()
        conn = self.connections.get(timeout=timeout)
        conn.ping(reconnect=True)
        return conn

    def return_resource(self, conn):
        if self.connections.full():
            self._close(conn)
            return
        self.connections.put(conn)

    @contextmanager
    def __call__(self, timeout=None):
        conn = self.get(timeout)
        try:
            yield conn.cursor()
            conn.commit()
        except:
            conn.rollback()
        finally:
            self.return_resource(conn)



if __name__ == '__main__':
    pool = ConnectionPool(host='127.0.0.1',
                          port=3306,
                          user='root',
                          password='123456',
                          database='demo',
                          cursorclass=DictCursor)
    # conn = pool.get()
    # try:
    #     with conn as cur:
    #         cur.execute('''select * from `author`''')
    #         for res in cur.fetchall():
    #             print(res)
    # finally:
    #     pool.return_resource(conn)

    # with pool() as conn:
    #     with conn as cur:
    #         cur.execute('''select * from `author`''')
    #         for res in cur.fetchall():
    #             print(res)

    with pool() as cur:
        cur.execute('''select * from `author`''')
        for res in cur.fetchall():
            print(res)