# -*- coding: utf-8 -*-
"""
指令处理模块,以 _0x 开头的函数为具体指令处理函数
入参数: (DeviceConnect, 指令参数)
       具体指令参数见通信文档
返回值: (模式, 参数)
模式有: send 发送参数数据
       recv 收到腕表指令
       last 与腕表交互最后一条指令
       stop 断开腕表长连接
"""
import logging
import setting
import gevent
from time import time
from bson.objectid import ObjectId
from core.db import db, redis, bluetooth_file
from struct import pack, error as pack_error
from random import choice
from core.proxy import Client
from core.buffer import CacheBuffer
from core.tools import set_watch_customer_id
from agent.alphabet import OK
from static.define import static_uri

logger = logging.getLogger('watch.instruct')
locate_proxy = Client(setting.LocateProxy['host'], setting.LocateProxy['port'])
push = Client(setting.push['host'], setting.push['port'])

# 星历文件下载链接
almanac_path = u'http://%s/almanac/current.alp' % static_uri
almanac_data = pack('>I', len(almanac_path.encode('utf-16-be'))) + almanac_path.encode('utf-16-be')
almanac_timeout = setting.server['almanac_timeout']
# 蓝牙版本下载链接
bluetooth_path = 'http://%s/bluetooth/%%s.bin' % static_uri
bluetooth_path_null = (bluetooth_path % ('0' * 24)).encode('utf-16-be')
bluetooth_path_length = len(bluetooth_path_null)

cache = CacheBuffer(expire=300)


def make_bluetooth_url(bluetooth_file_id, version):
    path = bluetooth_path % bluetooth_file_id
    return pack('>I%ssI' % bluetooth_path_length, bluetooth_path_length, path.encode('utf-16-be'), version)


def _0x01(conn, params):
    """
    腕表登陆
    腕表收到激活成功后,重新登录
    """
    imei, imsi, mac, heartbeat, software_v, bluetooth_v, customer_id = params
    logger.warning('%s relogin happed' % conn.imei)
    dev = conn.model
    dev.reload(retain=True)
    status = dev.status
    authcode = dev.authcode

    dev.imsi = imsi
    dev.heartbeat = heartbeat
    dev.software_v = software_v
    dev.bluetooth_v = bluetooth_v
    if dev.customer_id != customer_id:
        dev.customer_id = customer_id
        set_watch_customer_id(imei, customer_id)
    if dev.mac != mac:
        # mac 地址需要立即保存
        dev.mac = mac
        dev.save()
    data = pack('>BB10s', 1, status, authcode.encode('utf-16-be'))
    return 'send', data


def _0x02(conn, params):
    """
    腕表身份信息变化通知
    """
    return 'recv', 0


def _0x03(conn, params):
    """
    获取当前时间戳
    """
    return 'send', pack('>I4s', time(), '\x00\x00\x00\x08')


def _0x04(conn, params):
    """
    设置心跳间隔
    """
    return 'recv', 0


def _0x05(conn, params):
    """
    上传定位
    """
    locate_proxy.put(conn.imei, params)
    return 'send', ''


def _0x06(conn, params):
    """
    联系人列表变化通知
    """
    return 'recv', 0


def _0x07(conn, timestamp):
    """
    脱落报警
    """
    # FIXME 脱落报警
    # dev = conn.model
    # dev.reload(retain=True)
    # try:
    #     group_id = dev['group_id']
    #     message_id = db.message.insert_one({
    #         'type': 10,
    #         'group_id': group_id,
    #         'sender': dev['_id'],
    #         'sender_type': 2,
    #         'timestamp': timestamp,
    #     }).inserted_id
    #     push(1, group_id, {
    #         'push_type': 'talk',
    #         'group_id': group_id,
    #         'type': 10,
    #         'message_id': str(message_id),
    #         'sender': dev['_id'],
    #         'sender_type': 2,
    #         'timestamp': timestamp,
    #     })
    # except KeyError:
    #     pass
    return 'send', ''


def _0x08(conn, params):
    """
    激活腕表
    """
    conn.send('\x02', '')
    return 'recv', 0


def _0x0a(conn, params):
    """
    解绑腕表
    """
    return 'stop', 0


def _0x0b(conn, params):
    """
    腕表上传静音状态
    """
    # TODO 腕表静音状态
    return 'send', ''


def _0x0c(conn, params):
    """
    家庭圈新消息
    """
    return 'recv', 0


def _0x0e(conn, params):
    """
    请求持续定位
    """
    return 'recv', 0


def _0x10(conn, params):
    """
    结束持续定位
    """
    return 'recv', 0


def _0x12(conn, params):
    """
    锁定腕表
    """
    conn.model.status = 2
    conn.model.save()
    return 'recv', 0


def _0x14(conn, params):
    """
    解锁腕表
    """
    conn.model.status = 1
    conn.model.save()
    return 'recv', 0


def _0x16(conn, params):
    """
    监听腕表
    """
    monitor_status = conn.monitor_status
    if monitor_status != 0:
        conn.monitor_timestamp = time()
        if monitor_status == 1:
            conn.monitor_status = 2
            gevent.spawn(conn.monitor_wait)
    return 'recv', 0


def _0x17(conn, percent):
    """
    上传电量百分比
    :param percent: int类型,电量百分比0~100
    """
    if 15 <= percent <= 25:
        dev = conn.model
        dev.reload(retain=True)
        try:
            group_id = dev['group_id']
            timestamp = time()
            message_id = db.message.insert_one({
                'type': 6,
                'group_id': group_id,
                'percent': percent,
                'sender': dev['_id'],
                'sender_type': 2,
                'timestamp': timestamp,
            }).inserted_id
            push(1, group_id, {
                'message_id': str(message_id),
                'push_type': 'talk',
                'type': 6,
                'group_id': group_id,
                'percent': percent,
                'sender': dev['_id'],
                'sender_type': 2,
                'timestamp': timestamp,
            })
        except KeyError:
            pass
    return 'send', ''


def _0x18(conn, params):
    """
    腕表重新登陆
    """
    return 'stop', 0


def _0x1a(conn, params):
    """
    重启腕表
    """
    return 'stop', 0


def _0x1b(conn, params):
    """
    腕表低电量即将休眠
    """
    dev = conn.model
    dev.reload(retain=True)
    try:
        group_id = dev['group_id']
        timestamp = time()
        message_id = db.message.insert_one({
            'type': 11,
            'group_id': group_id,
            'sender': dev['_id'],
            'sender_type': 2,
            'timestamp': timestamp,
        }).inserted_id
        push(1, group_id, {
            'push_type': 'talk',
            'group_id': group_id,
            'type': 11,
            'message_id': str(message_id),
            'sender': dev['_id'],
            'sender_type': 2,
            'timestamp': timestamp,
        })
    except KeyError:
        pass
    return 'send', ''


def _0x1c(conn, params):
    """
    设置腕表飞行模式
    """
    return 'stop', 0


errno_message_type = {
    1: 8,  # 'watch_tf_limit'
    2: 9,  # 'watch_tf_error'
}


def _0x1d(conn, errno):
    """
    腕表上传错误代码
    """
    dev = conn.model
    dev.reload(retain=True)
    try:
        group_id = dev['group_id']
        timestamp = time()
        talk_type = errno_message_type[errno]
        message_id = db.message.insert_one({
            'type': talk_type,
            'group_id': group_id,
            'sender': dev['_id'],
            'sender_type': 2,
            'timestamp': timestamp,
        }).inserted_id
        push(1, group_id, {
            'push_type': 'talk',
            'group_id': group_id,
            'type': talk_type,
            'message_id': str(message_id),
            'sender': dev['_id'],
            'sender_type': 2,
            'timestamp': timestamp,
        })
    except KeyError:
        pass
    return 'send', ''


def _0x1e(conn, params):
    """
    设置腕表闹铃
    """
    return 'recv', 0


def locked(conn, user_id):
    result = conn.interact('\x12', '')
    if result == OK:
        group_id = conn.model['group_id']
        timestamp = time()
        message_id = db.message.insert_one({
            'type': 17,
            'group_id': group_id,
            'lock_status': 1,
            'imei': conn.imei,
            'sender': user_id,
            'sender_type': 1,
            'timestamp': timestamp,
        }).inserted_id
        push(1, group_id, {
            'message_id': str(message_id),
            'push_type': 'talk',
            'type': 17,
            'group_id': group_id,
            'lock_status': 1,
            'imei': conn.imei,
            'sender': user_id,
            'sender_type': 1,
            'timestamp': timestamp,
        })


def unlock(conn, user_id):
    result = conn.interact('\x14', '')
    if result == OK:
        group_id = conn.model['group_id']
        timestamp = time()
        message_id = db.message.insert_one({
            'type': 17,
            'group_id': group_id,
            'lock_status': 0,
            'imei': conn.imei,
            'sender': user_id,
            'sender_type': 1,
            'timestamp': timestamp,
        }).inserted_id
        push(1, group_id, {
            'message_id': str(message_id),
            'push_type': 'talk',
            'type': 17,
            'group_id': group_id,
            'lock_status': 0,
            'imei': conn.imei,
            'sender': user_id,
            'sender_type': 1,
            'timestamp': timestamp,
        })


codechar = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def _0x1f(conn, params):
    """
    腕表上传短信
    """
    phone, content = params
    dev = conn.model
    dev.reload(retain=True)
    try:
        group_id = dev['group_id']
    except KeyError:
        pass
    else:
        if content == 'XUNQUNRE':
            # 腕表收到APP请求恢复用户短信
            group = db.group.find_one({'_id': group_id}, {'users': 1})
            if not group:
                logger.warning("GROUP NOTFIND %s" % group_id)
                return 'send', ''
            for user_id, user in group.get('users', {}).items():
                if user.get('phone') == phone:
                    break
            else:
                logger.warning("PHONE %s NOTIN %s(%s) [XUNQUNRE]" % (phone, dev['_id'], group_id))
                return 'send', ''
            with redis.pipeline() as pipe:
                for i in range(10):
                    # 4位腕表验证码(英文大写)
                    code = ''.join([choice(codechar) for _ in range(4)])
                    if pipe.setnx('ResumeUser:%s' % code, user_id) \
                            .expire('ResumeUser:%s' % code, 900).execute()[0]:
                        conn.send('\x48', code.encode('utf-16-be'))
                        break
        elif content == 'XQLOCKED':
            # 锁定腕表
            status = dev.get('status', 0)
            if status != 2:
                group = db.group.find_one({'_id': group_id}, {'users': 1})
                if not group:
                    logger.warning("GROUP NOTFIND %s" % group_id)
                    return 'send', ''
                for user_id, user in group.get('users', {}).items():
                    if user.get('phone') == phone:
                        break
                else:
                    logger.warning("PHONE %s NOTIN %s(%s) [XQLOCKED]" % (phone, dev['_id'], group_id))
                    return 'send', ''
                gevent.spawn(locked, conn, user_id)
        elif content == 'XQUNLOCK':
            # 解锁腕表
            status = dev.get('status', 0)
            if status != 1:
                group = db.group.find_one({'_id': group_id}, {'users': 1})
                if not group:
                    logger.warning("GROUP NOTFIND %s" % group_id)
                    return 'send', ''
                for user_id, user in group.get('users', {}).items():
                    if user.get('phone') == phone:
                        break
                else:
                    logger.warning("PHONE %s NOTIN %s(%s) [XQUNLOCK]" % (phone, dev['_id'], group_id))
                    return 'send', ''
                gevent.spawn(unlock, conn, user_id)
        else:
            # 将短信内容发送至家庭圈
            timestamp = time()
            message_id = db.message.insert_one({
                'type': 7,
                'group_id': group_id,
                'phone': phone,
                'content': content,
                'sender': dev['_id'],
                'sender_type': 2,
                'timestamp': timestamp,
            }).inserted_id
            push(1, group_id, {
                'message_id': str(message_id),
                'push_type': 'talk',
                'type': 7,
                'group_id': group_id,
                'phone': phone,
                'content': content,
                'sender': dev['_id'],
                'sender_type': 2,
                'timestamp': timestamp,
            })
    return 'send', ''


def _0x20(conn, params):
    """
    发送故事给腕表
    """
    return 'recv', 0


def _0x22(conn, params):
    """
    删除腕表本地的故事
    """
    return 'recv', 0


def _0x24(conn, params):
    """
    设置腕表时间戳
    """
    return 'recv', 0


def _0x26(conn, params):
    """
    设置腕表一键拨号
    """
    return 'recv', 0


def _0x28(conn, params):
    """
    下发星历下载链接
    """
    return 'recv', 0


def _0x29(conn, recv_story_id):
    """
    腕表故事下载完毕反馈
    :param recv_story_id: str类型,24位长字符串, eg:55f43cb60bdb82a0fd9ff49c
    """
    story = db.story.find_one({'_id': ObjectId(recv_story_id)}, {'title': 1})
    dev = conn.model
    dev.reload(retain=True)
    try:
        group_id = dev['group_id']
        timestamp = time()
        content = u'收到故事《%s》' % story['title']
        message_id = db.message.insert_one({
            'type': 5,
            'group_id': group_id,
            'story_id': recv_story_id,
            'content': content,
            'status': 1,
            'sender': dev['_id'],
            'sender_type': 2,
            'timestamp': timestamp,
        }).inserted_id
        push(1, group_id, {
            'message_id': str(message_id),
            'push_type': 'talk',
            'type': 5,
            'group_id': group_id,
            'story_id': recv_story_id,
            'content': content,
            'status': 1,
            'sender': dev['_id'],
            'sender_type': 2,
            'timestamp': timestamp,
        })
    except KeyError:
        pass
    except TypeError:
        logger.warning('%s story not find' % recv_story_id)
    return 'send', ''


def _0x31(conn, params):
    """
    腕表请求星历下载信息
    """
    almanac_timestamp = cache.get('almanac_timestamp')
    try:
        return 'send', almanac_data + pack('>I', almanac_timestamp)
    except pack_error:
        alm_t = redis.get('AlmanacTimestamp')
        if alm_t:
            almanac_timestamp = int(alm_t)
            cache['almanac_timestamp'] = almanac_timestamp
            return 'send', almanac_data + pack('>I', almanac_timestamp)
    # 没有星历时间戳
    return 'send', almanac_data + '\x00\x00\x00\x00'


def _0x33(conn, params):
    """
    腕表主动关机
    """
    return 'last', ''


def _0x34(conn, params):
    """
    服务器下发关机指令
    """
    return 'stop', 0


def _0x35(conn, strategy):
    """
    腕表上传gps策略指令
    """
    # TODO 腕表上传gps策略指令
    return 'send', ''


def _0x36(conn, params):
    """
    服务器下发gps策略指令
    """
    gps_status = conn.gps_status
    if gps_status != 0:
        conn.gps_timestamp = time()
        if gps_status == 1:
            conn.gps_status = 2
            gevent.spawn(conn.gps_wait)
        if gps_status != 3:
            # 开启腕表gps后,请求腕表定位6次,每次10s
            conn.send('\x0e', '\x00\x06\x00\x0a')
    return 'recv', 0


def _0x37(conn, params):
    """
    腕表退出休眠模式
    """
    # TODO 腕表退出休眠
    return 'send', ''


def _0x38(conn, params):
    """
    家庭圈静默新消息
    """
    return 'recv', 0


def _0x3a(conn, params):
    """
    服务器开启腕表脱落告警
    """
    return 'recv', 0


def _0x3c(conn, params):
    """
    服务器关闭腕表脱落告警
    """
    return 'recv', 0


def _0x3d(conn, heartbeat):
    """
    腕表上传当前连接心跳值
    """
    conn.model.heartbeat = heartbeat
    return 'send', ''


def _0x3f(conn, params):
    """
    腕表上传当前gps状态
    """
    watch_star, catch_star, star_quality = params
    redis.hmset('Watch:%s' % conn.imei, {
        'watch_star': watch_star,
        'catch_star': catch_star,
        'star_quality': star_quality,
    })
    return 'send', ''


def _0x40(conn, params):
    """
    服务器返回腕表lbs定位坐标
    """
    return 'recv', 0


def _0x41(conn, params):
    """
    腕表请求下载蓝牙最新版本
    """
    content_file = cache.get('bluetooth_file')
    try:
        return 'send', make_bluetooth_url(content_file['_id'], content_file['version'])
    except TypeError:
        content_file = bluetooth_file.find_one(sort=[('uploadDate', -1)])
        if content_file:
            cache['bluetooth_file'] = {
                '_id': content_file._id,
                'version': content_file.version,
            }
            return 'send', make_bluetooth_url(content_file._id, content_file.version)
    # 没有蓝牙最新版本
    return 'send', pack('>I%ssI' % bluetooth_path_length, bluetooth_path_length, bluetooth_path_null, 0)


def _0x42(conn, params):
    """
    服务器下发蓝牙升级包地址
    """
    return 'recv', 0


def _0x43(conn, mac):
    """
    腕表上传激活用户的mac地址
    """
    user_id = redis.hmget('Watch:%s' % conn.imei, 'operator')
    if user_id:
        db.user.update_one({'_id': ObjectId(user_id)}, {'$set': {'mac': mac}})
    return 'send', ''


def _0x44(conn, params):
    """
    服务器下发答题游戏
    """
    return 'recv', 0


question_find_medal_id = {}


def build_question_to_medal():
    # init when watch server runing
    for medal in db.medal.find():
        for question_id in medal['question_list']:
            question_find_medal_id[question_id] = medal['_id']


def _0x45(conn, params):
    """
    腕表上传答题游戏结果
    """
    redis.hdel('Watch:%s' % conn.imei, 'answering')
    start_timestamp, end_timestamp, answer = params
    question_list = []
    result_list = []
    watch_answer = {
        'imei': conn.imei,
        'start_timestamp': start_timestamp,
        'end_timestamp': end_timestamp,
        'question_list': question_list,
        'result_list': result_list,
    }

    try:
        medal_question_id = answer[0][0]
    except IndexError:
        logger.warning('BAD ANSWER RESULT %s: %s' % (conn.imei, repr(params)))
        return 'send', ''
    medal_id = question_find_medal_id.get(medal_question_id)

    num = 0
    for result in answer:
        question_list.append(result[0])  # 问题id
        # result[1]  # 问题答案
        result_list.append(result[2])  # 答题情况(1:正确、0:错误)
        if result[2]:
            num += 1
    watch_answer['num'] = num
    db.watch_answer_game.insert(watch_answer)

    if medal_id and num == len(answer):
        # 该套题目是勋章答题且已全部答对
        db.watch.update_one({'_id': conn.imei}, {'$addToSet': {'medals': medal_id}})
    return 'send', ''


def _0x46(conn, params):
    """
    服务器设置腕表客户号
    """
    return 'recv', 0


def _0x48(conn, params):
    """
    服务器下发二维码
    """
    return 'recv', 0


def _0x4a(conn, params):
    """
    服务器下发腕表勋章墙
    """
    return 'recv', 0


def _0x4b(conn, finish_story_id):
    """
    腕表故事收听完毕反馈
    :param finish_story_id: str类型,24位长字符串, eg:55f43cb60bdb82a0fd9ff49c
    """
    story = db.story.find_one({'_id': ObjectId(finish_story_id)}, {'title': 1})
    dev = conn.model
    dev.reload(retain=True)
    try:
        group_id = dev['group_id']
        db.watch.update_one({'_id': dev['_id']}, {'$addToSet': {'storys': finish_story_id}})
        timestamp = time()
        content = u'读完故事《%s》' % story['title']
        message_id = db.message.insert_one({
            'type': 18,
            'group_id': group_id,
            'story_id': finish_story_id,
            'content': content,
            'status': 1,
            'sender': dev['_id'],
            'sender_type': 2,
            'timestamp': timestamp,
        }).inserted_id
        push(1, group_id, {
            'message_id': str(message_id),
            'push_type': 'talk',
            'type': 18,
            'group_id': group_id,
            'story_id': finish_story_id,
            'content': content,
            'status': 1,
            'sender': dev['_id'],
            'sender_type': 2,
            'timestamp': timestamp,
        })
    except KeyError:
        pass
    except TypeError:
        logger.warning('%s story not find' % finish_story_id)
    return 'send', ''
