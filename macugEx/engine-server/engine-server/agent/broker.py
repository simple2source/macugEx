# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_socket()
import zmq.green as zmq
import gevent
import time
from gevent.queue import Queue, Empty
from os import urandom
from alphabet import (WORKERTIME, FINDONE, SENDBLOCK, SENDNOBLOCK, GETLIST, GETTOTAL, HEARTBEAT, FINDTIMEOUT,
                      DEMANDTIMEOUT, OK, NO, TIMEOUT)

ctx = zmq.Context()


class Publish(object):
    def __init__(self, socket):
        self._sock = socket
        self.task = Queue()
        self._started = False

    def send(self, command):
        self.task.put(command)

    def recv(self):
        while 1:
            command = self.task.get()
            self._sock.send_multipart(command)

    def start(self):
        if self._started:
            raise RuntimeError("Publish already start.")
        gevent.spawn(self.recv)
        self._started = True


class Route(object):
    def __init__(self, socket, handle=None):
        """
        :param socket: ZMQ's socket
        :param handle: ROUTE socket handle
                def handle(message):
                    identify,_,payload = message
                    ...
                    return [identify,'',data]
        """
        if not handle:
            raise RuntimeError("Route need handle's method to dispatch request")
        self._sock = socket
        self.task = Queue()
        self._started = False
        self.handle = handle

    def handle_task(self, message):
        result = self.handle(message)
        if result:
            self.task.put(result)

    def send_loop(self):
        while 1:
            message = self.task.get()
            self._sock.send_multipart(message)

    def recv_loop(self):
        while 1:
            message = self._sock.recv_multipart()
            gevent.spawn(self.handle_task, message)

    def start(self):
        if self._started:
            raise RuntimeError("Route already start.")
        gevent.spawn(self.send_loop)
        gevent.spawn(self.recv_loop)
        self._started = True


class RequestQueue(object):
    def __init__(self, size=5):
        self._queue = []
        for i in range(size):
            self._queue.append(Queue())

    def acquire(self):
        try:
            q = self._queue.pop()
        except IndexError:
            q = Queue()
        return q

    def release(self, q):
        q.queue.clear()
        self._queue.append(q)


class Broker(object):
    def __init__(self, host, request_port, respound_port, channel_port, check_period=WORKERTIME, log=None):
        if not log:
            raise RuntimeError("Broker need logging.")
        self.log = log

        request_sock = ctx.socket(zmq.ROUTER)
        request_sock.bind("tcp://%s:%d" % (host, request_port))
        self.request = Route(request_sock, self.request_handle)

        dispose_sock = ctx.socket(zmq.ROUTER)
        dispose_sock.bind("tcp://%s:%d" % (host, respound_port))
        self.dispose = Route(dispose_sock, self.dispose_handle)

        publish_sock = ctx.socket(zmq.PUB)
        publish_sock.bind("tcp://%s:%d" % (host, channel_port))
        self.publish = Publish(publish_sock)

        self.workers = {}
        self.check_period = check_period
        self.client_result = {}
        self.update_lock = True

        self.request_message = {
            FINDONE: self._request_FINDONE,
            SENDBLOCK: self._request_SENDBLOCK,
            GETLIST: self._request_GETLIST,
            GETTOTAL: self._request_GETTOTAL,
        }
        self.dispose_message = {
            FINDONE: self._dispose_FINDONE,
            SENDBLOCK: self._dispose_SENDBLOCK,
            HEARTBEAT: self._dispose_HEARTBEAT,
            GETLIST: self._dispose_GETLIST,
            GETTOTAL: self._dispose_GETTOTAL,
        }

        self.request_queue = RequestQueue()

    def _request_FINDONE(self, box):
        for _ in self.workers.keys():
            temp = box.get(timeout=FINDTIMEOUT)
            if temp == OK:
                return OK
        return NO

    def _request_SENDBLOCK(self, box):
        exist = 0
        for _ in self.workers.keys():
            temp = box.get(timeout=DEMANDTIMEOUT)
            # 超时时间与Demand的超时时间相同
            if temp == OK:
                return OK
            elif temp == TIMEOUT:
                exist = 1
        if not exist:
            return NO
        else:
            return TIMEOUT

    def _request_GETLIST(self, box):
        result = []
        for _ in self.workers.keys():
            # 超时时间与查找的超时时间相同
            result.extend(box.get(timeout=FINDTIMEOUT))
        return result

    def _request_GETTOTAL(self, box):
        total = 0
        for _ in self.workers.keys():
            # 超时时间与查找的超时时间相同
            total += int(box.get(timeout=FINDTIMEOUT))
        return str(total)

    def request_handle(self, message):
        """
        message is [client_id, '', instruct, ...(extra data)]
        """
        client_id = message[0]
        instruct = message[2]

        if instruct == SENDNOBLOCK:
            # 广播指令给dispose,不需要回复
            self.publish.send(message)
            return [client_id, '', OK]

        client_ident = client_id + urandom(5)
        q = self.request_queue.acquire()
        self.client_result[client_ident] = q
        message[0] = client_ident
        self.publish.send(message)
        try:
            result = self.request_message[instruct](q)
        except Empty:
            # dispose回应超时
            self.log.warning('dispose respound too slow')
            self.update_workers()
            if instruct == GETLIST:
                return [client_id, '', '']
            elif instruct == GETTOTAL:
                return [client_id, '', '0']
            else:
                return [client_id, '', TIMEOUT]
        finally:
            del self.client_result[client_ident]
            self.request_queue.release(q)
        if isinstance(result, list):
            # GETLIST 指令
            if result:
                return [client_id, ''] + result
            else:
                return [client_id, '', '']
        else:
            return [client_id, '', result]

    def _dispose_HEARTBEAT(self, worker_id, data):
        self.workers[worker_id] = time.time()

    def _dispose_FINDONE(self, worker_id, data):
        try:
            client_ident = data[0]
            box = self.client_result[client_ident]
            box.put(data[1])
        except KeyError:
            return None

    def _dispose_SENDBLOCK(self, worker_id, data):
        try:
            client_ident = data[0]
            box = self.client_result[client_ident]
            box.put(data[1])
        except KeyError:
            return None

    def _dispose_GETLIST(self, worker_id, data):
        try:
            client_ident = data[0]
            box = self.client_result[client_ident]
            box.put(data[1:])
        except KeyError:
            return None

    def _dispose_GETTOTAL(self, worker_id, data):
        try:
            client_ident = data[0]
            box = self.client_result[client_ident]
            box.put(data[1])
        except KeyError:
            return None

    def dispose_handle(self, message):
        """
        message is [worker_id, '', COMMAND, ...(extra data)]
        """
        worker_id = message[0]
        instruct = message[2]
        data = message[3:]
        self.dispose_message[instruct](worker_id, data)
        return [worker_id, '', OK]

    def update_workers(self):
        if self.update_lock:
            self.update_lock = False
            self.workers.clear()
            self.publish.send(['', '', HEARTBEAT])
            gevent.sleep(2)
            self.update_lock = True

    def _start(self):
        self.publish.start()
        self.request.start()
        self.dispose.start()

    def run(self):
        self._start()
        while 1:
            gevent.sleep(self.check_period)
            now = time.time()
            for w, wtime in self.workers.items():
                if now - wtime >= self.check_period:
                    del self.workers[w]
