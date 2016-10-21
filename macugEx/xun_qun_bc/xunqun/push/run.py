# -*- coding: utf-8 -*-
from gevent import monkey, get_hub

monkey.patch_all(Event=True, dns=False)
from gevent.server import StreamServer
import gevent
import msgpack
import struct
import json
import logging
from logging.handlers import RotatingFileHandler
import sys
import ssl
import socket

sys.path.append('..')
import setting
from mqtt import push_mqtt
from apns import push_apns
from core.db import redis
from core.tools import clean_user_redis

user_channel = '%s/user/' % setting.mqtt['prefix'] + '%s'
group_channel = '%s/group/' % setting.mqtt['prefix'] + '%s'


def text_message(data):
    data['content'] = data['content'].decode('utf-8')
    return None


def story_status(data):
    data['content'] = data['content'].decode('utf-8')
    return None


def low_battery(data):
    return {'alert': u'手表低电量', 'sound': 'default', 'data': data}


def watch_sms(data):
    data['content'] = data['content'].decode('utf-8')
    return None


def tf_limit(data):
    return {'alert': u'手表存储卡容量不足', 'sound': 'default', 'data': data}


def tf_error(data):
    return {'alert': u'手表存储卡读取异常', 'sound': 'default', 'data': data}


def watch_falling(data):
    return {'alert': u'手表脱落告警', 'sound': 'default', 'data': data}


def watch_sleep(data):
    return {'alert': u'手表进入休眠模式', 'sound': 'default', 'data': data}


def user_enter(data):
    data['user_name'] = data['user_name'].decode('utf-8')
    return {'alert': u'新成员进入圈子', 'sound': 'default', 'data': data}


def user_leave(data):
    return {'alert': u'有成员离开圈子', 'sound': 'default', 'data': data}


def watch_enter(data):
    data['dev_name'] = data['dev_name'].decode('utf-8')
    return {'alert': u'新手表进入圈子', 'sound': 'default', 'data': data}


def watch_leave(data):
    return {'alert': u'有手表离开圈子', 'sound': 'default', 'data': data}


def watch_lock_status(data):
    if data.get('lock_status') == 1:
        return {'alert': u'手表已被锁定', 'sound': 'default', 'data': data}
    else:
        return {'alert': u'手表已被解锁', 'sound': 'default', 'data': data}


def story_has_read(data):
    data['content'] = data['content'].decode('utf-8')
    return None


group_talk_handle = {
    # 1: audio_message,  # 家庭圈语音消息
    # 2: image_message,  # 家庭圈图片消息
    3: text_message,  # 家庭圈文字消息
    # 4: watch_locus,  # 腕表新轨迹点
    5: story_status,  # 故事反馈消息
    6: low_battery,  # 腕表低电量消息
    7: watch_sms,  # 腕表新短信消息
    8: tf_limit,  # 腕表存储卡容量不足
    9: tf_error,  # 腕表存储卡读取异常
    10: watch_falling,  # 腕表脱落告警
    11: watch_sleep,  # 腕表低电量进入休眠
    12: user_enter,  # 新成员进入圈子
    13: user_leave,  # 有成员离开圈子
    14: watch_enter,  # 新手表进入圈子
    15: watch_leave,  # 有手表离开圈子
    # 16: watch_updown_status,  # 腕表上下线消息
    17: watch_lock_status,  # 腕表加解锁消息
    18: story_has_read,  # 故事已读反馈消息
}


def handle(pack):
    """
    push_type, push_id, data = msgpack.unpackb(pack, use_list=0)

    push_type: 推送类型
                1: 圈子, 2: 用户, 3: 用户列表
    push_id:   推送id,
                group_id || user_id
    data:      推送数据
                {
                    'type': <type>
                    ...
                }
    """
    push_type, push_id, data = msgpack.unpackb(pack, use_list=0)
    apns_params = None

    if data['push_type'] == 'talk':
        if data['type'] in group_talk_handle:
            apns_params = group_talk_handle[data['type']](data)
    elif data['push_type'] == 'watch_locate':
        # 手表定位
        if data['locus'] == 1:
            # 手表新定位轨迹点
            data['address'] = data['address'].decode('utf-8')
    elif data['push_type'] == 'service' and data.get('action') == 1:
        apns_params = {'alert': u'您的问题已有客服人员处理', 'sound': 'default', 'data': data}

    if apns_params:
        apns_is_silent = 0
    else:
        # 默认推送参数为 静默推送
        apns_params = {'content_available': 1, 'data': data}
        apns_is_silent = 1

    if push_type == 1:
        push_mqtt(group_channel % push_id, json.dumps(data))

        if data['push_type'] == 'talk' and data['sender_type'] == 1:
            block_user_id = data['sender']
        else:
            block_user_id = ''

        for user_id in redis.smembers('GroupAppleUser:%s' % push_id):
            if user_id != block_user_id:
                token, ident, version, focus = redis.hmget('User:%s' % user_id, 'app_token', 'app_ident', 'app_version',
                                                           'app_focus')
                if token and (not focus or not apns_is_silent):
                    gevent.spawn(push_apns, {'token': token, 'ident': ident, 'version': version}, apns_params)
                    if not apns_is_silent:
                        # FIXME 非静默推送同时,推送一个静默推送的版本
                        gevent.spawn(push_apns, {'token': token, 'ident': ident, 'version': version},
                                     {'content_available': 1, 'data': data})
    elif push_type == 2:
        token, ident, version, focus = redis.hmget('User:%s' % push_id,
                                                   'app_token', 'app_ident', 'app_version', 'app_focus')
        if token and (not focus or not apns_is_silent):
            push_apns({'token': token, 'ident': ident, 'version': version}, apns_params)
            if not apns_is_silent:
                # FIXME 非静默推送同时,推送一个静默推送的版本
                push_apns({'token': token, 'ident': ident, 'version': version},
                          {'content_available': 1, 'data': data})
        else:
            push_mqtt(user_channel % push_id, json.dumps(data))
    elif push_type == 3:
        for user_id in push_id:
            token, ident, version, focus, clean = redis.hmget('User:%s' % user_id,
                                                              'app_token', 'app_ident', 'app_version', 'app_focus',
                                                              'clean')
            if token and (not focus or not apns_is_silent):
                gevent.spawn(push_apns, {'token': token, 'ident': ident, 'version': version}, apns_params)
                if not apns_is_silent:
                    # FIXME 非静默推送同时,推送一个静默推送的版本
                    gevent.spawn(push_apns, {'token': token, 'ident': ident, 'version': version},
                                 {'content_available': 1, 'data': data})
            else:
                push_mqtt(user_channel % user_id, json.dumps(data))

            if clean:
                # 删除后用户没有圈子,将用户redis数据下线
                clean_user_redis(user_id)

    logger.info('%s: %s' % (push_id, repr(data)))


def sock_handle(sock, address):
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
                gevent.spawn(handle, pack)
            sock.send('\x00')
    except socket.error:
        pass
    except:
        logger.error('', exc_info=True)


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if exc_type not in (ssl.SSLEOFError, ssl.SSLError, socket.error, KeyboardInterrupt):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


logger = logging.getLogger('push')
logfile = setting.push['logfile']
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=50)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
File_logging.setLevel(setting.push['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(setting.push['loglevel'])

if __name__ == '__main__':
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    host = '0.0.0.0' if setting.push['host'] != '127.0.0.1' else '127.0.0.1'
    server = StreamServer(('127.0.0.1', setting.push['port']), sock_handle, backlog=100000)
    server.serve_forever()
