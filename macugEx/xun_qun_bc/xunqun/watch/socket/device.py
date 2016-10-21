# -*- coding: utf-8 -*-
"""
腕表连接处理模块,处理该腕表指令与交互细节
在run模块中,已经处理socket登陆细节
还包含DeviceDict,DeviceStat全局信息字典
"""
import socket
from gevent.event import AsyncResult
from gevent.event import Timeout
from random import randint, choice
from struct import pack
from bson import Binary
from bson.objectid import InvalidId
from pymongo.cursor import CursorType
import logging
import instruct
import setting
import gevent
import time
from packet import extract, assemble
from instruct import make_bluetooth_url
from agent.alphabet import OK, NO, TIMEOUT, DISPOSETIMEOUT
from agent.client import Demand, Dispose
from core.db import db, redis, put_dev_job, bluetooth_file
from core.buffer import CacheBuffer
from core.tools import create_watch, set_watch_customer_id
from static.define import chars, static_uri
from core.proxy import Client
from model import ModelProxy, ModelNotExist

logger = logging.getLogger('watch.device')
agent = Demand(setting.broker['host'], setting.broker['request_port'])
push = Client(setting.push['host'], setting.push['port'])

almanac_path = u'http://%s/almanac/current.alp' % static_uri
almanac_data = pack('>I', len(almanac_path.encode('utf-16-be'))) + almanac_path.encode('utf-16-be')
almanac_timeout = setting.server['almanac_timeout']

cache = CacheBuffer(expire=300)

__all__ = ['DeviceConnect', 'device_upon', 'device_offs']

dispatch = {chr(int(iterm[-2:], 16)): getattr(instruct, iterm) for iterm in dir(instruct) if iterm.startswith('_0x')}

# 腕表监听指令有效时间
monitor_waittime = 30
# 号码'0000'用于关闭腕表监听指令
phone_0000 = '\x00\x00\x00\x08\x00\x30\x00\x30\x00\x30\x00\x30'
# 腕表开机即发送默认的 gps 设置离线指令
gps_default_job = {'instruct': '\xf6', 'data': '\x01'}
gps_starting_job = {'instruct': '\xf6', 'data': '\x02'}
gps_remain_timestamp = 180

DeviceDict = {}
DeviceStat = {}


def device_upon(address, imei, dc):
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
        try:
            group_id = dc.model['group_id']
            timestamp = time.time()
            message_id = db.message.insert_one({
                'type': 16,
                'group_id': group_id,
                'status': 1,
                'sender': imei,
                'sender_type': 2,
                'timestamp': timestamp,
            }).inserted_id
            push(1, group_id, {
                'message_id': str(message_id),
                'push_type': 'talk',
                'type': 16,
                'group_id': group_id,
                'status': 1,
                'sender': imei,
                'sender_type': 2,
                'timestamp': timestamp,
            })
        except KeyError:
            pass
        logger.debug('imei:%s upon %r' % (imei, address))


def device_offs(address, imei):
    # finally 结束后由gevent关闭连接
    # dc.stop()
    logger.debug('imei:%s offs %r' % (imei, address))
    try:
        if address == DeviceStat[imei]:
            dev = DeviceDict[imei].model
            del DeviceDict[imei]
            dev.reload(retain=True)
            try:
                group_id = dev['group_id']
                timestamp = time.time()
                message_id = db.message.insert_one({
                    'type': 16,
                    'group_id': group_id,
                    'status': 2,
                    'sender': dev['_id'],
                    'sender_type': 2,
                    'timestamp': timestamp,
                }).inserted_id
                push(1, group_id, {
                    'message_id': str(message_id),
                    'push_type': 'talk',
                    'type': 16,
                    'group_id': group_id,
                    'status': 2,
                    'sender': dev['_id'],
                    'sender_type': 2,
                    'timestamp': timestamp,
                })
            except KeyError:
                pass
    except KeyError:
        logger.warning('%s already offline' % imei)
    except ModelNotExist:
        # 腕表被删除后下线
        pass


def interact(imei, instruct, data):
    """
    返回 OK, NO, TIMEOUT 返回成功、失败、超时
    """
    try:
        conn = DeviceDict[imei]
    except KeyError:
        return NO
    result = conn.interact(instruct, data)
    return result


def sendtodev(imei, instruct, data):
    """
    返回值忽略
    """
    if imei in DeviceDict:
        DeviceDict[imei].send(instruct, data)


def generate_dispose():
    return Dispose(DeviceDict, setting.broker['host'], setting.broker['respond_port'],
                   setting.broker['channel_port'], interact=interact, interact_noblock=sendtodev)


def watch_loger(event, imei, itype, data):
    if isinstance(data, str):
        db.watch_loger.insert_one(
            {'imei': imei, 'event': event, 'itype': ord(itype), 'data': Binary(data), 'timestamp': time.time()})
    else:
        db.watch_loger.insert_one(
            {'imei': imei, 'event': event, 'itype': ord(itype), 'data': data, 'timestamp': time.time()})


def get_watch_jobbox(imei, gps_start=0):
    """
    usage:
        job_list = get_watch_jobbox
        for job in job_list:
            result = self.interact(job['instruct'], job['data'])
    """
    jobbox = list(db.watch_jobbox.find({'imei': imei}).sort('timestamp', 1).limit(100))
    if jobbox:
        page = 0
        message_job = []
        message_job_start = 0
        reduced_job = {}
        while jobbox:
            for job in jobbox:
                itype = str(job['instruct'])
                job['instruct'] = itype
                # 在离线指令中除了 '\x0c'(圈子消息) 之外,都可以被合并发送
                if itype == '\x08':
                    pass
                elif itype != '\x0c':
                    reduced_job[itype] = job
                elif message_job_start:
                    # 腕表有多个离线圈子消息时,除了第一条外,其他的为静音的圈子消息('\x38')
                    job['instruct'] = '\x38'
                    message_job.append(job)
                else:
                    message_job.append(job)
                    message_job_start = 1
            if len(jobbox) >= 100:
                page += 1
                jobbox = list(db.watch_jobbox.find({'imei': imei}).sort('timestamp', 1).skip(page * 100).limit(100))
            else:
                # 所有离线指令都已经取完
                jobbox = tuple()
        if '\xf6' not in reduced_job:
            reduced_job['\xf6'] = gps_starting_job if gps_start else gps_default_job
        # 其他消息优先发送,圈子消息只接收最后二十条
        return reduced_job.values() + message_job[-20:]
    else:
        return gps_starting_job if gps_start else gps_default_job,


class DeviceConnect(object):
    __slots__ = ('_sock', '_status', '_recv_inbox', '_extra_data', 'imei',
                 'model',  # 连接对象所使用的数据库缓存
                 'gps_timestamp',  # 腕表gps最后一次开启时间
                 'gps_status',  # 腕表gps启动状态,0:未开启腕表gps,1:已发送腕表开启gps指令,2:已收到腕表开启gps指令确认
                 'monitor_timestamp',  # 腕表监听最后一次开启时间
                 'monitor_status',  # 腕表监听状态,0:未启动腕表监听,1:已发送腕表监听指令,2:已收到腕表监听指令确认
                 )

    def __init__(self, sock, imei):
        self._sock = sock
        self._status = True
        # 指令发送队列
        self._recv_inbox = {}
        # 指令接收字典
        self.imei = imei
        self.model = ModelProxy(imei=imei)
        self.gps_status = 0
        self.gps_timestamp = 0
        self.monitor_status = 0
        self.monitor_timestamp = 0

    def login(self, identify, serverip, params):
        watch_loger('recv', self.imei, '\x01', params)
        imei, imsi, mac, heartbeat, software_v, bluetooth_v, customer_id = params
        dev = self.model
        now = time.time()
        if dev.check_document_exist():
            change = 0
            try:
                status = dev['status']
            except KeyError:
                logger.warning('not status %s' % imei)
                for group in db.group.find({'devs.%s' % imei: {'$exists': True}}, {'devs': 1},
                                           cursor_type=CursorType.EXHAUST):
                    if imei in group.get('devs', tuple()):
                        if group['devs'][imei].get('status'):
                            status = dev.status = 1
                            break
                else:
                    status = dev.status = 3
                change = 1
            authcode = dev.authcode
            if not authcode:
                logger.warning('not authcode %s' % imei)
                authcode = dev.authcode = ''.join([choice(chars) for _ in range(5)])
                redis.hset('Watch:%s' % imei, 'authcode', authcode)
                change = 1
            dev.heartbeat = heartbeat
            dev.imsi = imsi
            dev.serverip = serverip
            dev.software_v = software_v
            dev.bluetooth_v = bluetooth_v
            if dev.customer_id != customer_id:
                dev.customer_id = customer_id
                set_watch_customer_id(imei, customer_id)
            if dev.mac != mac:
                # mac 地址需要立即保存
                dev.mac = mac
                change = 1
            dev.lasttime = now
            if change:
                dev.save()
        else:
            authcode = ''.join([choice(chars) for _ in range(5)])
            status, watch = create_watch(imei, now=now, update={
                'imsi': imsi,
                'mac': mac,
                'heartbeat': heartbeat,
                'serverip': serverip,
                'authcode': authcode,
                'customer_id': customer_id,
            })
            object.__setattr__(dev, '_data', watch)

        data = pack('>BB10s', 1, status, authcode.encode('utf-16-be'))
        self.send('\x01', data, identify=identify)

    def login_handle(self):
        imei = self.imei
        now = time.time()
        # 根据上次gps开启时间设置当前连接的默认gps指令
        gps_start_timestamp = self.model.gps_start_timestamp
        if gps_start_timestamp:
            if (gps_start_timestamp + gps_remain_timestamp) > now:
                gps_start = 1
            else:
                self.model.gps_start_timestamp = 0
                gps_start = 0
        else:
            gps_start = 0

        job_list = get_watch_jobbox(imei, gps_start=gps_start)
        if job_list:
            faild_job_id_list = []
            for job in job_list:
                result = self.interact(job['instruct'], job['data'])
                if result != OK:
                    if job['instruct'] != '\xf6':
                        # 除了gps设置指令,其他指令需要继续重发
                        faild_job_id_list.append(job['_id'])
            db.watch_jobbox.delete_many({'_id': {'$nin': faild_job_id_list}, 'imei': imei})

        last_t = self.model.last_almanac_timestamp
        if not last_t or now - last_t > almanac_timeout:  # 腕表超过一段时间没有下载过星历
            almanac_timestamp = cache.get('almanac_timestamp')
            if almanac_timestamp:
                # update watch almanac
                result = self.interact('\x28', almanac_data + pack('>I', almanac_timestamp))
                if result == OK:
                    self.model.last_almanac_timestamp = now
            else:
                alm_t = redis.get('AlmanacTimestamp')
                if alm_t:
                    almanac_timestamp = int(alm_t)
                    cache['almanac_timestamp'] = almanac_timestamp
                    # update watch almanac
                    result = self.interact('\x28', almanac_data + pack('>I', almanac_timestamp))
                    if result == OK:
                        self.model.last_almanac_timestamp = now

        last_bluetooth = cache.get('bluetooth_file')
        if not last_bluetooth:
            bluetooth = bluetooth_file.find_one(sort=[('uploadDate', -1)])
            if bluetooth:
                cache['bluetooth_file'] = {
                    '_id': bluetooth._id,
                    'version': bluetooth.version,
                }
                if self.model.bluetooth_v < bluetooth.version:
                    result = self.interact('\x42', make_bluetooth_url(bluetooth._id, bluetooth.version))
                    if result == OK:
                        self.model.bluetooth_v = bluetooth.version
        elif self.model.bluetooth_v < last_bluetooth['version']:
            result = self.interact('\x42', make_bluetooth_url(last_bluetooth['_id'], last_bluetooth['version']))
            if result == OK:
                self.model.bluetooth_v = last_bluetooth['version']

    def gps_wait(self):
        # gps_start_timestamp需要在agent中发送,不能用浮点类型
        gps_start_timestamp = int(time.time())
        self.model.gps_start_timestamp = gps_start_timestamp
        self.model.save()
        remind_time = gps_remain_timestamp
        while remind_time > 0:
            gevent.sleep(remind_time)
            spend_time = time.time() - self.gps_timestamp
            if spend_time >= gps_remain_timestamp:
                if self.reliable_close_gps(gps_start_timestamp) == 1:
                    # 关闭腕表gps策略,删除腕表上次开启时的搜星状态
                    self.gps_status = 0
                    self.gps_timestamp = 0
                    self.model.gps_start_timestamp = 0
                else:
                    # 腕表不在线后,直接操作数据库进行更新 gps_start_timestamp
                    db.watch.update_one({'_id': self.imei}, {'$set': {'gps_start_timestamp': 0}})
                redis.hdel('Watch:%s' % self.imei, 'watch_star', 'catch_star', 'star_quality')
                return
            else:
                remind_time = gps_remain_timestamp - spend_time

    def monitor_wait(self):
        remind_time = monitor_waittime
        while remind_time > 0:
            gevent.sleep(remind_time)
            spend_time = time.time() - self.monitor_timestamp
            if spend_time >= monitor_waittime:
                self.reliable_delivery('\x16', phone_0000)
                self.monitor_status = 0
                self.monitor_timestamp = 0
                redis.hdel('Watch:%s' % self.imei, 'monitor_user_id')
                return None
            else:
                remind_time = monitor_waittime - spend_time

    def reliable_close_gps(self, gps_start_timestamp):
        """
        关闭腕表gps,将开启时的gps_timestamp传入指令,用于连接对象判断该次发送是否过期
        """
        if self.interact('\x36', '\x01') != OK:
            # 本腕表连接已断线,在向新的腕表连接发送时
            # 转换指令类型以区分发送给自身的指令与开机发送的默认指令
            if interact(self.imei, '\xe6', gps_start_timestamp) != OK:
                if agent.send(self.imei, '\xe6', str(gps_start_timestamp)) != OK:
                    return 4
                else:
                    return 3
            else:
                return 2
        else:
            return 1

    def reliable_delivery(self, itype, data):
        """
        可靠地向腕表发送数据,失败时存储到离线任务
        :param itype: <str>  指令编码  '\x01'
        :param data: <list>  指令数据
        :return < OK or NO >
        """
        if self.interact(itype, data) != OK:
            if interact(self.imei, itype, data) != OK:
                if agent.send(self.imei, itype, data) != OK:
                    put_dev_job(self.imei, itype, data)
                    return NO
        return OK

    def loop(self):
        try:
            while self._status:
                version, identify, itype, params, self._extra_data = extract(self._sock, self._extra_data)
                self.handle(identify, itype, params)
        except socket.error:
            pass
        except InvalidId:
            logger.error('%s InvalidId %s' % (self.imei, repr(params)), exc_info=True)
        except ModelNotExist:
            logger.error(self.imei + ' Model Not Find.', exc_info=True)
        finally:
            self.stop()

    def handle(self, identify, itype, params):
        """
        处理腕表指令
        :param identify: 指令编号
        :param itype: 指令类型
        :param params: 参数
        """
        watch_loger('recv', self.imei, itype, params)

        pattern, data = dispatch[itype](self, params)
        if pattern == 'send':
            self.send(itype, data, identify=identify)
        else:
            if identify in self._recv_inbox:
                self._recv_inbox[identify].set(1)
            if pattern == 'last':
                self.send(itype, data, identify=identify)
                self.stop()
            elif pattern == 'stop':
                self.stop()
                # elif pattern == 'recv':
                #     pass

    def send(self, itype, data, identify=None, need_respond=0):
        """
        请求腕表确认时identify为空
        """
        if itype == '\x36':
            if data == '\x02' and (self.gps_status == 0 or self.gps_status == 3):
                # 请求开启腕表gps状态且当前未开启gps
                self.gps_status = 1
            elif data == '\x01' and self.gps_status != 0:
                # 请求关闭gps状态且当前已经开启gps
                self.gps_status = 3
        elif itype == '\x16' and str(data) != phone_0000 and self.monitor_status == 0:
            # 开启腕表监听指令且当前未开启监听
            self.monitor_status = 1
        elif itype == '\xf6':
            # 腕表每次连线的默认设置gps指令
            if self.gps_status != 0:
                # 当前若已开启gps,忽略该关闭指令
                return None
            itype = '\x36'
        elif itype == '\xe6':
            # 腕表上次开启了gps,该指令是上次的关闭指令
            if self.gps_status != 0:
                # 当前若已开启gps,忽略该关闭指令
                return None
            if self.model.gps_start_timestamp and int(data) < self.model.gps_start_timestamp:
                # 当前关闭指令的时间戳不是当前最新的时间戳,忽略该次关闭
                return None
            itype = '\x36'
            data = '\x01'

        watch_loger('send', self.imei, itype, data)

        if not identify:
            identify = pack('>H', randint(0, 65535))
        if need_respond:
            self._recv_inbox[identify] = AsyncResult()

        self._sock.sendall(assemble(identify, itype, data))
        return identify

    def interact(self, itype, data):
        """
        向终端发送数据,并等待确认
        :param itype: <str>  指令编码  '\x01'
        :param data: <list>  指令数据
        """
        if not self._status:
            return NO

        identify = self.send(itype, data, need_respond=1)
        if not identify:
            # 该指令已被自定义处理,返回成功
            return OK
        try:
            self._recv_inbox[identify].get(timeout=DISPOSETIMEOUT)
            result = OK
        except Timeout:
            result = TIMEOUT
        finally:
            del self._recv_inbox[identify]
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
