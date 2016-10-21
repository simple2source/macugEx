# -*- coding: utf-8 -*-
"""
if monkey.patch_all() then will be :

...
clock_gettime(CLOCK_MONOTONIC, {3132171, 133287677}) = 0
gettimeofday({1444992908, 879938}, NULL) = 0
gettimeofday({1444992908, 880040}, NULL) = 0
gettimeofday({1444992908, 880140}, NULL) = 0
gettimeofday({1444992908, 880228}, NULL) = 0
clock_gettime(CLOCK_MONOTONIC, {3132171, 133780668}) = 0
clock_gettime(CLOCK_MONOTONIC, {3132171, 133901728}) = 0
epoll_wait(4, {}, 64, 1)

cpu occupancy rate least 3%
"""
from gevent import monkey, get_hub

monkey.patch_all(Event=True, dns=False)
from gevent.server import StreamServer
import gevent
import msgpack
import struct
import time
import logging
from logging.handlers import RotatingFileHandler
import sys
import ssl
import socket

try:
    import ujson as json
except ImportError:
    import json

sys.path.append('../..')
import setting
from agent.client import Demand
from core.db import db, redis
from core.proxy import Client
from core.misc import distance
from handle import raw_gps_convert, lbs_request, geo_request, get_last_gps_locus, new_last_gps_locus, \
    get_last_lbs_locus, new_last_lbs_locus, get_request_user

push = Client(setting.push['host'], setting.push['port'])
agent = Demand(setting.broker['host'], setting.broker['request_port'])

gps_loger = 'db.watch_gps_loger.find({"imei":"%s"}).sort({"timestamp": -1}).limit(1).forEach(' \
            'function(doc){db.watch_gps_loger.update({"_id": doc._id}, {"$set": {' \
            '"recv_timestamp": %f,' \
            '"spendtime": (%f - doc.timestamp),' \
            '"loc": [%f, %f],' \
            '"address": "%s"' \
            '}})})'


def handle(pack):
    imei, args = msgpack.unpackb(pack, use_list=0)
    raw_locate_reply, raw_lon, raw_lat, gps_timestamp, lbs, lbs_timestamp = args
    # 定位类型,1:GPS,2:LBS
    locate_type = 1 if raw_lat and raw_lon else 2
    # 定位指令时间,有GPS时取GPS时间戳
    timestamp = gps_timestamp if locate_type == 1 else lbs_timestamp
    # 默认不取redis缓存
    redis_data = None

    if locate_type == 1:
        # GPS原始经纬度转换
        status, result = raw_gps_convert(raw_lon, raw_lat)
        if not status:
            return None
        lon, lat, address, province, city, citycode, adcode = result
        radius = 0
    elif lbs:
        # LBS数据解析
        status, result = lbs_request(imei, lbs)
        if not status:
            return None
        lon, lat, radius, address, province, city, citycode, adcode = result
    else:
        logger.error('LBS info required %s: %s' % (imei, repr(args)))
        return None

    if raw_locate_reply == 1:
        # 腕表上传心跳定位
        if locate_type == 2:
            # 腕表上传心跳定位且只含lbs数据时,返回腕表当前解析到的高德经纬度
            data = struct.pack('>24s24sI',
                               (str(lon) + '0' * (24 - len(str(lon)))).encode('utf-16-be'),
                               (str(lat) + '0' * (24 - len(str(lat)))).encode('utf-16-be'),
                               lbs_timestamp)
            agent.send(imei, '\x40', data)
    else:
        # 腕表响应服务器请求定位指令
        if not redis_data:
            redis_data = redis.hgetall('Watch:%s' % imei)
        will_delete_key = []
        if 'group_id' in redis_data:
            if 'request_gps_users' in redis_data and locate_type == 1:
                push(3, redis_data['request_gps_users'].split(','), {
                    'push_type': 'watch_locate',
                    'locus': 0,
                    'type': 1,
                    'imei': imei,
                    'radius': radius,
                    'lon': lon,
                    'lat': lat,
                    'timestamp': timestamp,
                })
                will_delete_key.append('request_gps_users')
            elif 'request_lbs_users' in redis_data:
                if locate_type == 1:
                    if lbs:
                        status, result = lbs_request(imei, lbs)
                        if not status:
                            return None
                        lbs_lon, lbs_lat, lbs_radius = result[:3]
                    else:
                        logger.error('LBS info required %s: %s' % (imei, repr(args)))
                        return None
                else:
                    lbs_lon, lbs_lat, lbs_radius = lon, lat, radius
                push(3, redis_data['request_lbs_users'].split(','), {
                    'push_type': 'watch_locate',
                    'locus': 0,
                    'type': 2,
                    'imei': imei,
                    'radius': lbs_radius,
                    'lon': lbs_lon,
                    'lat': lbs_lat,
                    'timestamp': lbs_timestamp,
                })
                will_delete_key.append('request_lbs_users')
        if 'gps_logging' in redis_data and locate_type == 1:
            if not address:
                status, result = geo_request(lon, lat, raw_lon, raw_lat)
                if not status:
                    return None
                address, province, city, citycode, adcode = result
            now = time.time()
            # unicode字符与str % 之后为unicode,bson.code.Code需要 str
            db.eval(gps_loger % (imei, now, now, lon, lat, address.encode('utf-8')))
            will_delete_key.append('gps_logging')
        if will_delete_key:
            redis.hdel('Watch:%s' % imei, *will_delete_key)

    # 判断是否有新轨迹点
    has_new_locus = 0
    # 腕表定位指令时间
    raw_struct_time = time.gmtime(timestamp)
    if locate_type == 1:
        last_gps_locus = get_last_gps_locus(imei)
        if not last_gps_locus:
            # 没有获取到上次gps定位轨迹
            has_new_locus = 1
        elif last_gps_locus['struct_time'].tm_yday != raw_struct_time.tm_yday:
            # 上次的gps轨迹点日期和这次定位的不同
            has_new_locus = 1
        elif distance(lon, lat, last_gps_locus['lon'], last_gps_locus['lat']) > 50:
            # gps距离超过50m
            last_lbs_locus = get_last_lbs_locus(imei)
            if not last_lbs_locus:
                has_new_locus = 1
            elif last_lbs_locus['timestamp'] - timestamp <= 180 and \
                            distance(lon, lat, last_lbs_locus['lon'], last_lbs_locus['lat']) > \
                            last_lbs_locus['lbs_radius']:
                # 和上次3分钟内的lbs轨迹点的距离超过该轨迹点半径
                logger.warning('GPS %s: %s,%s too far for %s' % (imei, lon, lat, repr(last_lbs_locus)))
                if lbs:
                    status, result = lbs_request(imei, lbs)
                    if not status:
                        return None
                    lbs_lon, lbs_lat, lbs_radius = result[:3]
                    if distance(lon, lat, lbs_lon, lbs_lat) > lbs_radius:
                        # 和当前用lbs 数据得到的距离超过该定位点半径
                        logger.warning('GPS %s: %s,%s too far with %s,%s' % (imei, lon, lat, lbs_lon, lbs_lat))
                        if distance(lbs_lon, lbs_lat, last_lbs_locus['lon'], last_lbs_locus['lat']) > \
                                last_lbs_locus['radius']:
                            # 当前lbs 定位可以得到轨迹点,转换定位类型
                            has_new_locus = 1
                            locate_type = 0
                            lon, lat, radius, address, province, city, citycode, adcode = result
                    else:
                        has_new_locus = 1
                else:
                    has_new_locus = 1
            else:
                has_new_locus = 1
    else:
        # 获取上次lbs定位轨迹
        last_lbs_locus = get_last_lbs_locus(imei)
        if not last_lbs_locus:
            # 没有获取到上次lbs定位轨迹
            has_new_locus = 1
        elif last_lbs_locus['struct_time'].tm_yday != raw_struct_time.tm_yday:
            # 上次的轨迹点日期和这次定位的不同
            has_new_locus = 1
        elif distance(lon, lat, last_lbs_locus['lon'], last_lbs_locus['lat']) > last_lbs_locus['radius']:
            # 距离超过轨迹半径,生成轨迹点
            has_new_locus = 1

    if has_new_locus:
        # 轨迹点间有效半径,100~200以内,看定位的精度
        locus_radius = max(min(radius, 200), 50)
        if locate_type == 1:
            new_last_gps_locus(imei, lon, lat, raw_struct_time, timestamp)
        else:
            new_last_lbs_locus(imei, lon, lat, raw_struct_time, timestamp, locus_radius, radius)
        if not redis_data:
            redis_data = redis.hgetall('Watch:%s' % imei)
        group_id = redis_data.get('group_id')
        if group_id:
            # 生成轨迹信息,圈子轨迹信息
            if locate_type == 1 and not address:
                status, result = geo_request(lon, lat, raw_lon, raw_lat)
                if not status:
                    return None
                address, province, city, citycode, adcode = result
            locus = {
                'imei': imei,
                'type': locate_type,
                'lon': lon,
                'lat': lat,
                'address': address,
                'radius': locus_radius,
                'timestamp': timestamp,
            }
            if locate_type != 1:
                locus['lbs_radius'] = radius
            db.watch_locus.insert_one(locus)
            # FIXME 推送轨迹点到有需要的用户
            push_user_list = get_request_user(redis_data)
            if push_user_list:
                push(3, push_user_list, {
                    'push_type': 'watch_locate',
                    'type': locate_type,
                    'locus': 1,
                    'imei': imei,
                    'lon': lon,
                    'lat': lat,
                    'radius': locus_radius,
                    'address': address,
                    'timestamp': timestamp,
                })

    # 保存腕表定位数据
    locate = {
        'imei': imei,
        'type': locate_type,
        'loc': [lon, lat],
        'radius': radius,
        'timestamp': timestamp,
    }
    if address:
        locate['address'] = address
        locate['province'] = province
        locate['city'] = city
        locate['citycode'] = citycode
        locate['adcode'] = adcode
    if locate_type == 1:
        locate['raw_loc'] = [raw_lon, raw_lat]
    db.watch_locate.insert_one(locate)


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


logger = logging.getLogger('LocateProxy')
logfile = setting.LocateProxy['logfile']
File_logging = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=50)
File_logging.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
File_logging.setLevel(setting.LocateProxy['loglevel'])
logger.addHandler(File_logging)
logger.setLevel(setting.LocateProxy['loglevel'])


def sys_exc_hook(exc_type, exc_value, exc_tb):
    if exc_type not in (KeyboardInterrupt,):
        logger.critical('sys exception traceback', exc_info=(exc_type, exc_value, exc_tb))


def gevent_exc_hook(context, exc_type, exc_value, exc_tb):
    if exc_type not in (ssl.SSLEOFError, ssl.SSLError, socket.error, KeyboardInterrupt):
        logger.critical('gevent exception traceback', exc_info=(exc_type, exc_value, exc_tb))


if __name__ == '__main__':
    sys.excepthook = sys_exc_hook
    get_hub().print_exception = gevent_exc_hook
    host = '0.0.0.0' if setting.LocateProxy['host'] != '127.0.0.1' else '127.0.0.1'
    server = StreamServer((host, setting.LocateProxy['port']), sock_handle, backlog=1024)
    server.serve_forever()
