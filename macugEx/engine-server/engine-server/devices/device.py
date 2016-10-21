# -*- coding: utf-8 -*-
"""
腕表连接处理模块,处理该腕表指令与交互细节
在run模块中,已经处理socket登陆细节
还包含DeviceDict,DeviceStat全局信息字典
"""
from gevent import socket
from gevent.event import AsyncResult
from gevent.event import Timeout
from random import randint
from bson.objectid import InvalidId
import logging
import instruct
import conf
import time
import json
from packet import extract, assemble
from agent.alphabet import OK, NO, TIMEOUT, DISPOSETIMEOUT
from agent.client import Demand, Dispose
from core.db import db, dump_pending_task
from model import ModelProxy, ModelNotExist

logger = logging.getLogger('watch.device')
agent = Demand(conf.agent['host'], conf.agent['request_port'])

__all__ = ['DeviceConnect', 'device_upon', 'device_offs']

dispatch = {int(iterm[5:]): getattr(instruct, iterm) for iterm in dir(instruct) if iterm.startswith('type_')}

DeviceDict = {}
DeviceStat = {}


def device_upon(address, imei, dc):
    imei = str(imei)
    try:
        stale_dc = DeviceDict[imei]
        stale_dc.stop()
        # logger.warning('%s already in DeviceDict' % imei)
    except KeyError:
        pass
    except socket.error:
        pass
    finally:
        DeviceDict[imei] = dc
        DeviceStat[imei] = address
        logger.debug('imei:%s upon %r' % (imei, address))


def device_offs(address, imei):
    # finally 结束后由gevent关闭连接
    imei = str(imei)
    try:
        if address == DeviceStat[imei]:
            del DeviceDict[imei]
    except KeyError:
        logger.warning('%s already offline' % imei)
    except ModelNotExist:
        # 腕表被删除后下线
        pass
    finally:
        logger.debug('imei:%s offs %r' % (imei, address))


def interact(imei, data):
    """
    返回 OK, NO, TIMEOUT 返回成功、失败、超时
    """
    try:
        conn = DeviceDict[imei]
    except KeyError:
        return NO
    result = conn.interact(json.loads(data))
    return result


def sendtodev(imei, data):
    """
    返回值忽略
    """
    if imei in DeviceDict:
        DeviceDict[imei].send(json.loads(data))


def generate_dispose():
    return Dispose(DeviceDict, conf.agent['host'], conf.agent['respond_port'],
                   conf.agent['port'], interact=interact, interact_noblock=sendtodev)


def logger_to_db(event, imei, data):
    db.device_loger.insert_one(
        {'imei': imei, 'event': event, 'type': data.get('type', 0), 'data': data, 'timestamp': time.time()})


def get_device_tasks(imei):
    """
    usage:
        task_list = get_device_tasks
        for task in task_list:
            result = self.interact(task['data'])
    """
    tasks = list(db.pending_tasks.find({'imei': imei}).sort('timestamp', 1).limit(100))
    if tasks:
        page = 0
        reduced_job = {}
        while tasks:
            for task in tasks:
                reduced_job[task['itype']] = task
            if len(tasks) >= 100:
                page += 1
                tasks = list(db.pending_tasks.find({'imei': imei}).sort('timestamp', 1).skip(page * 100).limit(100))
            else:
                # 所有离线指令都已经取完
                tasks = tuple()
        return reduced_job.values()
    else:
        return tuple()


class DeviceConnect(object):
    __slots__ = ('_sock', '_status', '_recv_inbox', '_extra_data', 'imei',
                 'model',  # 连接对象所使用的数据库缓存
                 )

    def __init__(self, sock, imei):
        self._sock = sock
        self._status = True
        # 指令发送队列
        self._recv_inbox = {}
        # 指令接收字典
        self.imei = imei
        self.model = ModelProxy(imei=imei)

    def login(self, ident, serverip, data):
        logger_to_db('recv', self.imei, data)
        self.send({'type': 1, 'status': 200}, ident=ident)

    def login_handle(self):
        imei = self.imei
        now = time.time()
        self.model.lasttime = now
        if not self.model.check_document_exist():
            self.model.maketime = now
            self.model.save()

        task_list = get_device_tasks(imei)
        if task_list:
            faild_job_id_list = []
            for task in task_list:
                result = self.interact(task['data'])
                if result != OK:
                    faild_job_id_list.append(task['_id'])
            db.pending_tasks.delete_many({'_id': {'$nin': faild_job_id_list}, 'imei': imei})

    def reliable_delivery(self, data):
        """
        可靠地向设备发送数据,失败时存储到离线任务
        :param itype: <str>  指令编码  '\x01'
        :param data: <list>  指令数据
        :return < OK or NO >
        """
        if self.interact(data) != OK:
            if interact(self.imei, data) != OK:
                if agent.send(self.imei, data) != OK:
                    dump_pending_task(self.imei, data)
                    return NO
        return OK

    def loop(self):
        try:
            while self._status:
                data, self._extra_data = extract(self._sock, self._extra_data)
                self.handle(data)
        except socket.error:
            pass
        except InvalidId:
            logger.error('%s InvalidId %s' % (self.imei, repr(data)), exc_info=True)
        except ModelNotExist:
            logger.error(self.imei + ' Model Not Find.', exc_info=True)
        finally:
            self.stop()

    def handle(self, data):
        """
        处理腕表指令
        :param data: 指令数据
        """
        logger_to_db('recv', self.imei, data)
        itype = data.get('type')
        ident = data.get('ident')

        if itype in dispatch:
            pattern, data = dispatch[itype](self, data)
            if pattern == 'send':
                data.update({'type': itype, 'ident': ident})
                self.send(data, ident=ident)
            else:
                if ident in self._recv_inbox:
                    self._recv_inbox[ident].set(1)
                if pattern == 'last':
                    data.update({'type': itype, 'ident': ident})
                    self.send(data, ident=ident)
                    self.stop()
                elif pattern == 'stop':
                    self.stop()
            return None
        self.send(data, ident=ident)

    def send(self, data, ident=None, need_respond=0):
        """
        请求腕表确认时 ident 为空
        :param data: 发送数据
        :param ident: 指令序号
        :param need_respond: 是否为设备待确认指令
        :return: 指令序号
        """
        logger_to_db('send', self.imei, data)

        if not data.get('ident'):
            data['ident'] = ident if ident else randint(0, 65535)

        ident = data['ident']
        if need_respond:
            self._recv_inbox[ident] = AsyncResult()

        self._sock.sendall(assemble(data))
        return ident

    def interact(self, data):
        """
        向终端发送数据,并等待确认
        :param data: <list>  指令数据
        """
        if not self._status:
            return NO

        ident = self.send(data, need_respond=1)
        if not ident:
            # 该指令已被自定义处理,返回成功
            return OK
        try:
            self._recv_inbox[ident].get(timeout=DISPOSETIMEOUT)
            result = OK
        except Timeout:
            result = TIMEOUT
        finally:
            del self._recv_inbox[ident]
        return result

    def stop(self):
        """
        self._sock.shutdown 有可能会失败,需要先设置 _status
        """
        if self._status:
            self._status = False
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()

    def __repr__(self):
        return '<CONNECT %s>' % self.imei

    def __del__(self):
        self.stop()
