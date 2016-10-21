# -*- coding: utf-8 -*-
"""
APP, Watch, Admin, push 之间通用的工具类函数
"""
from datetime import datetime
from random import choice
from static.define import chars
from db import db, redis
from time import time
from bson.objectid import ObjectId


def create_watch(imei, update=None, now=None):
    """
    usage:
        status, watch = create_watch(imei, update=update)
    status:
        用于自定义的返回腕表激活状态,未用到
    watch:
        所创建的腕表数据字典
    """
    if not now:
        now = time()
    if update is None:
        status = 3
    else:
        if 'authcode' not in update:
            update['authcode'] = ''.join([choice(chars) for _ in range(5)])

        if 'status' in update:
            status = update['status']
        else:
            status = 3
    data = {
        '_id': imei,
        'lasttime': now,
        'maketime': datetime.fromtimestamp(now),
        'customer_id': 0,
        'status': status,
    }
    for k, v in update.items():
        data[k] = v
    redis.hmset('Watch:%s' % imei, {
        'authcode': data['authcode'],
        'customer_id': data['customer_id'],
    })
    result = db.watch.update_one({'_id': imei}, {'$set': data}, upsert=True)
    # FIXME result检查
    return status, data


def set_watch_customer_id(imei, customer_id):
    redis.hset('Watch:%s' % imei, 'customer_id', customer_id)


def set_user_session(session_key, user_id, extra=None):
    __set_user_session(session_key, user_id)
    if isinstance(extra, dict):
        extra['session'] = session_key
        redis.hmset('User:%s' % user_id, extra)
    else:
        redis.hset('User:%s' % user_id, 'session', session_key)


def __set_user_session(session_key, user_id):
    redis.hset('Session:%s' % session_key[:3], session_key[3:], user_id)


def del_session(session_key):
    return redis.hdel('Session:%s' % session_key[:3], session_key[3:])


def clean_user_redis(user_id):
    redis_data = {}
    backup_user_struct(user_id, copy_if_need=redis_data)
    redis.delete('User:%s' % user_id)
    if 'session' in redis_data:
        del_session(redis_data['session'])


def backup_user_struct(user_id, copy_if_need=None):
    """
    若backup后删除用户redis数据,则需要将session数据也删除
    """
    user = redis.hgetall('User:%s' % user_id)
    if isinstance(copy_if_need, dict):
        for i, j in user.items():
            copy_if_need[i] = j
    if user:
        if isinstance(user_id, (str, unicode)):
            user_id = ObjectId(user_id)
        db.user.update_one({'_id': user_id}, {'$set': user})


def restore_user_struct(user_id, user=None):
    if isinstance(user_id, (str, unicode)):
        user_id = ObjectId(user_id)
    if not user:
        user = db.user.find_one({'_id': user_id},
                                {'session': 1, 'app_token': 1, 'app_ident': 1, 'app_version': 1, 'groups': 1})
    if user:
        update = {}
        if 'app_token' in user:
            update['app_token'] = user['app_token']
        if 'app_ident' in user:
            update['app_ident'] = user['app_ident']
        if 'app_version' in user:
            update['app_version'] = user['app_version']
        if 'groups' in user:
            update['groups'] = user['groups']
        if 'session' in user:
            set_user_session(user['session'], user_id, extra=update)
        if update:
            redis.hmset('User:%s' % user_id, update)
