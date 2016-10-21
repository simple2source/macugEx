# -*- coding: utf-8 -*-
"""
to adaptation Client behavior, Server socket handle Snippet.
try:
    extra = ''
    sock.settimeout(900)
    while 1:
        if len(extra) < 4:
            data = sock.recv(4096)
            if not data:
                raise socket.error
            if extra:
                data = extra + data
            length, = struct.unpack('>I', data[:4])
            data = data[4:]
        else:
            length, = struct.unpack('>I', extra[:4])
            data = extra[4:]
        if len(data) < length:
            while len(data) < length:
                complement = sock.recv(4096)
                if not complement:
                    raise socket.error
                data += complement
        pack = data[:length]
        extra = data[length:]
        if pack:
            Greenlet.spawn(handle, pack).start()
        sock.send('\x00')
except socket.error:
    pass
except:
    logger.error('', exc_info=True)
"""
import gevent
from gevent import socket
from gevent import queue as Queue
import msgpack
import struct


class Client(object):
    def __init__(self, host, port, queue=None, keepalive=600, retry_time=10, start_num=1):
        self.address = (host, port)
        self.pedding = []
        self.started = 0
        if queue:
            self.queue = queue
        else:
            self.queue = Queue.Queue(maxsize=4096)
        self.keepalive = keepalive
        self.retry_time = retry_time
        if start_num:
            self.spawn(start_num)

    def __call__(self, *data):
        try:
            self.queue.put_nowait(data)
        except Queue.Full:
            self.queue.queue.clear()
            self.queue.put(data)

    def put(self, *data):
        try:
            self.queue.put_nowait(data)
        except Queue.Full:
            self.queue.queue.clear()
            self.queue.put(data)

    def handle_queue(self, sock):
        data = ''
        sock.settimeout(20)
        while 1:
            try:
                data = self.queue.get(timeout=self.keepalive)
                pack = msgpack.packb(data)
                pack_length = struct.pack('>I', len(pack))
                sock.sendall(pack_length + pack)
                _ = sock.recv(1)
                if not _:
                    raise socket.error
            except Queue.Empty:
                # keep a live heartbeat
                try:
                    sock.sendall('\x00\x00\x00\x00')
                    _ = sock.recv(1)
                    if not _:
                        raise socket.error
                except socket.error:
                    self.started -= 1
                    self.spawn(1)
                    break
            except socket.error:
                if data:
                    self.queue.put(data)
                self.started -= 1
                self.spawn(1)
                break

    def make_client(self):
        sock = socket.socket()
        sock.connect(self.address)
        gevent.spawn(self.handle_queue, sock)

    def _spawn(self):
        while len(self.pedding) > 0:
            try:
                self.make_client()
                self.pedding.pop()
                self.started += 1
            except socket.error:
                gevent.sleep(self.retry_time)

    def spawn(self, num):
        self.pedding.extend(list(range(num)))
        if self.started < len(self.pedding):
            gevent.spawn(self._spawn)
