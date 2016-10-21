# -*- coding: utf-8 -*-
"""
模拟器类
"""
import threading
import socket

try:
    import Queue
except ImportError:
    import queue as Queue
import datetime
import logging
import random
import struct
import click
import time
import json


def pack_data(data):
    package = json.dumps(data)
    pkd_length = len(package)
    pkg_length = struct.pack('>I', pkd_length)
    return pkg_length + package


class Emulate(object):
    def __init__(self, host='127.0.0.1', port=8000, imei=355372020827303, heartbeat=300, log=None):
        self.address = (host, port)
        self.imei = imei
        self.heartbeat = heartbeat
        self._sock = None
        self._queue = Queue.Queue()
        self.loop_started = 0
        if not log:
            self.logger = logging.getLogger('devices.emulate')
            printlog = logging.StreamHandler()
            printlog.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            printlog.setLevel(logging.DEBUG)
            self.logger.addHandler(printlog)
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger = log

        self.connect()
        self.login()

    def connect(self):
        self._sock = socket.socket()
        self._sock.connect(self.address)
        return self._sock

    def login(self):
        self.send({'type': 1, 'imei': str(self.imei), 'heartbeat': self.heartbeat})

    def send(self, data, ident=None):
        if not data.get('ident'):
            if ident is None:
                data['ident'] = random.randint(0, 65535)
            else:
                data['ident'] = ident
        self.logger.info('send: %s' % repr(data))
        if self.loop_started:
            self._queue.put(data)
        else:
            self._sock.send(pack_data(data))

    def _send(self):
        while True:
            data = self._queue.get()
            if not data:
                return None
            self._sock.send(pack_data(data))

    def recv(self):
        pack = self._sock.recv(4)
        if not pack:
            raise socket.error
        length = struct.unpack('>I', pack)[0]
        if length:
            data = self._sock.recv(length)
            if not data:
                raise socket.error
            return json.loads(data)
        else:
            raise RuntimeError('Emulate receive bad package header')

    def heartbeat_loop(self):
        while 1:
            time.sleep(self.heartbeat)
            self.send({'type': 3})

    def _loop(self):
        send_thread = threading.Thread(target=self._send)
        send_thread.daemon = True
        send_thread.start()
        self.loop_started = 1
        try:
            while 1:
                self.action(self.recv())
        except socket.error:
            self.logger.info('%s socket terminate' % datetime.datetime.now())
        finally:
            self._queue.put(None)

    def loop(self, block=True):
        heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
        if block:
            self._loop()
        else:
            recv_thread = threading.Thread(target=self._loop)
            recv_thread.daemon = True
            recv_thread.start()

    def action(self, data):
        # itype = data['type']
        # ident = data['ident']
        # self.send({'type': itype, 'ident': ident})
        self.logger.info('recv: %s' % repr(data))


@click.command()
@click.option('-h', '--host', default='127.0.0.1', help='server host')
@click.option('-p', '--port', default=8000, help='server port')
@click.option('--imei', default=355372020827303, help='emulate imei')
@click.option('-H', '--heartbeat', default=300, help='emulate heartbeat')
def main(host, port, imei, heartbeat):
    emulate = Emulate(host=host, port=port, imei=imei, heartbeat=heartbeat)

    # 指令发送示例

    # emulate.send({
    #     'type': 999,
    #     'data': 'abcdef'
    # })

    emulate.send({'tyd': 2})

    emulate.loop()


if __name__ == '__main__':
    main()
