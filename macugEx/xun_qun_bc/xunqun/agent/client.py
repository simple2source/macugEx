# -*- coding: utf-8 -*-
import zmq.green as zmq
from gevent import Timeout
import gevent
from alphabet import (DEMANDTIMEOUT, SENDBLOCK, SENDNOBLOCK, FINDONE, GETLIST, GETTOTAL, HEARTBEAT,
                      HEARTBEATTIME, DISPOSETIMEOUT, OK, NO, TIMEOUT)

ctx = zmq.Context()


class REQClient(object):
    """
    ClientPoll's Client(thread unsafe object)
    """

    # TODO add context manage for automation release back parent Poll

    def __init__(self, host, port):
        _sock = ctx.socket(zmq.REQ)
        _sock.connect("tcp://%s:%d" % (host, port))
        self._sock = _sock

    def send(self, request):
        """
        :param request: [COMMAND, ...(extra data)]
        """
        self._sock.send_multipart(request)

    def recv(self):
        """
        :return [RESULT, ...(extra data)]
        """
        return self._sock.recv_multipart()


class ClientPool(object):
    def __init__(self, host, port):
        """
        redis's ConnectionPool default max_connection is 2**31
        so nearly dont't worry about ClientPool haven't max_size
        """
        self._idle_clients = []
        self.host = host
        self.port = port

    def get_client(self):
        try:
            client = self._idle_clients.pop()
        except IndexError:
            # client = self.make_client()
            client = REQClient(self.host, self.port)
        return client

    # def make_client(self):
    #     if self._current_size >= self.max_size:
    #         raise Exception("Too many connections")
    #     self._current_size += 1
    #     return DemandClient()

    def release(self, client):
        self._idle_clients.append(client)


class Demand(object):
    def __init__(self, request_host, request_port, timeout=DEMANDTIMEOUT):
        self.pool = ClientPool(request_host, request_port)
        self.timeout = timeout

    def _request(self, request):
        """
        request is list like [COMMAND, deviceId, ...(extra data)]
        1.request --> broker
        2.broker  --> dispose
        3.dispose --> broker
        4.broker --> request
        """
        client = self.pool.get_client()
        client.send(request)
        try:
            with Timeout(self.timeout):
                result = client.recv()
        except Timeout:
            # 正常不应该超时,只有与broker通信缓慢时出现
            del client
            return [TIMEOUT]
        else:
            self.pool.release(client)
            return result

    def send(self, imei, instruct, data):
        return self._request([SENDBLOCK, str(imei), instruct, data])[0]

    def send_nowait(self, imei, instruct, data):
        return self._request([SENDNOBLOCK, str(imei), instruct, data])[0]

    def find(self, imei):
        return self._request([FINDONE, str(imei)])[0]

    def getlist(self, page, num):
        return self._request([GETLIST, str(page), str(num)])

    def gettotal(self):
        return self._request([GETTOTAL])[0]


class Dispose(object):
    def __init__(self, resource, host, respound_port, channel_port, heartbeat=HEARTBEATTIME, interact=None,
                 interact_noblock=None):
        """
        broker default ttl 15s,us heartbeat 10s
        resource are Dict to find device,is Big Dict!
        interact,interact_noblock function will like:

        def interact(imei, instruct, params):
            if imei not in resource:
                return NO
            try:
                ...
                return OK
            except Timeout:
                return TIMEOUT

        def interact_noblock(imei, instruct, params):
            if imei in resource:
                ...
            return None
        """
        if not isinstance(resource, dict):
            raise RuntimeError('Dispose resource need Dict to find Device')
        if not callable(interact):
            raise RuntimeError('interact must be callable')
        if not callable(interact_noblock):
            raise RuntimeError('interact_noblock must be callable')

        # _sock = ctx.socket(zmq.REQ)
        # _sock.connect("tcp://%s:%d" % (host, respound_port))
        # self._sock = _sock
        self.pool = ClientPool(host, respound_port)

        sub = ctx.socket(zmq.SUB)
        sub.connect("tcp://%s:%d" % (host, channel_port))
        sub.setsockopt(zmq.SUBSCRIBE, '')
        self._sub = sub
        self.heartbeat = heartbeat
        self.resource = resource
        self.interact = interact
        self.interact_noblock = interact_noblock

    def _handle(self, message):
        # print message
        client_id = message[0]
        instruct = message[2]
        data = message[3:]
        if instruct == SENDBLOCK:
            imei = data[0]
            if imei in self.resource:
                try:
                    with Timeout(DISPOSETIMEOUT):
                        result = self.interact(*data)
                        # result must be OK,NO,TIMEOUT
                        self.send([instruct, client_id, result])
                except Timeout:
                    self.send([instruct, client_id, TIMEOUT])
            else:
                self.send([instruct, client_id, NO])
            return None
        elif instruct == SENDNOBLOCK:
            self.interact_noblock(*data)
            return None
        elif instruct == GETLIST:
            page = int(data[0])
            num = int(data[1])
            devicelist = self.resource.keys()[page * num:(page + 1) * num]
            respond = [instruct, client_id]
            respond.extend(devicelist)
            self.send(respond)
            return None
        elif instruct == GETTOTAL:
            self.send([instruct, client_id, str(len(self.resource))])
            return None
        elif instruct == FINDONE:
            if data[0] in self.resource:
                self.send([instruct, client_id, OK])
            else:
                self.send([instruct, client_id, NO])
            return None
        elif instruct == HEARTBEAT:
            self.send([HEARTBEAT])

    def handle_publish(self):
        while 1:
            message = self._sub.recv_multipart()
            gevent.spawn(self._handle, message)

    def send(self, message):
        client = self.pool.get_client()
        client.send(message)
        client.recv()
        self.pool.release(client)
        # self._sock.send_multipart(message)
        # self._sock.recv_multipart()

    def loop(self):
        while 1:
            self.send([HEARTBEAT])
            gevent.sleep(self.heartbeat)

    def start(self):
        gevent.spawn(self.handle_publish)
        gevent.spawn(self.loop)
