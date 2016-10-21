# -*- coding: utf-8 -*-
"""
APP的视图函数路由
用'api_<URL>'开头的函数,挂载到 '/v1/<URL>'
接口编码过程中,data为表单类处理过的字典,所有字段至少都有值
从mongodb取出的数据字典不可信任,要用get方法获取字典数据
"""
from __future__ import absolute_import
from gevent.event import AsyncResult
from flask import request
from functools import wraps
from operator import itemgetter
from pymongo.helpers import DuplicateKeyError
from bson.objectid import InvalidId
from Crypto.Cipher import AES
from werkzeug.wrappers import Response
from copy import deepcopy
from agent.alphabet import NO
from core.buffer import CacheBuffer
from core.misc import distance
from core.tools import create_watch, set_user_session
from static.define import *
from static.tools import *
import calendar
import binascii
import datetime

from . import form
from .tools import *
from .mantain import get_banner_list, get_category_list, get_hot_list, get_random_game_list, get_game_category_list, \
    get_medal_list, get_medal_question_list

import sys

if sys.version_info.major < 3:
    range = xrange

db_name = setting.mongo['database']


def succed(data=None):
    r = Response(headers=[('Content-Type', 'application/json')])
    if data is not None:
        r.data = json.dumps({'status': 200, 'data': data})
    else:
        r.data = '{"status":200,"data":{}}'
    return r


def failed(code=0, fail_info=None):
    r = Response(headers=[('Content-Type', 'application/json')])
    if fail_info:
        if isinstance(fail_info, (list, tuple)):
            field, debug = fail_info
            r.data = '{"status":300,"data":{"error":"%d","field":"%s","debug":"%s"}}' % (
                code, field, debug.replace('"', "'"))
        else:
            r.data = '{"status":300,"data":{"error":"%d","debug":"%s"}}' % (
                code, fail_info.replace('"', "'"))
    else:
        r.data = '{"status":300,"data":{"error":"%d"}}' % code
    return r


def validate_decorator(validator):
    def decorator(func):
        @wraps(func)
        def apiv1_request_wrapper(*args, **kwargs):
            request_form = request.json if request.mimetype == 'application/json' else request.form if \
                request.form else json.loads(request.data) if request.data else {}
            status, data = validator.validate(request_form)
            if status:
                if data.get('session'):
                    user_id = get_session_user_id(data['session'])
                    if not user_id:
                        return failed(E_session)
                    data['session_user_id'] = user_id
                kwargs['data'] = data
                return func(*args, **kwargs)
            else:
                return failed(E_params, data)

        return apiv1_request_wrapper

    return decorator


@validate_decorator(form.GroupCreate())  # 创建圈子和用户
def api_group_create(data):
    now_date = datetime.datetime.now()
    now = time.mktime(now_date.timetuple())
    session_key = generate_session()
    if not data['user_name']:
        data['user_name'] = generate_user_name()
    if not data['group_name']:
        data['group_name'] = generate_group_name()

    group_id = generate_group_id()
    user = {
        'maketime': now_date,
        'session': session_key,
        'name': data['user_name'],
        'group_id': group_id,
        'group_name': data['group_name'],
        'type': 1,
    }
    if data['user_image']:
        u_image_id = user_image_put(data['user_image'])
        user['image_id'] = u_image_id
    if data['identify']:
        user['app_ident'] = data['identify']
    if not data['password']:
        data['password'] = generate_group_password()
    # if data['face_image']:
    #     status, face = face_upload(data['face_image'])
    #     if not status:
    #         return failed(E_face_image_umatch)
    #     user_face_image_id = user_face.put(data['face_image'])
    #     face_id = face['face_id']
    #     user['faces'] = {str(user_face_image_id): face}
    #     user['face_images'] = [user_face_image_id]

    # pymongo将insert的 user 自动添加一个_id键, 后面可以使用 user['_id']
    user_id = str(db.user.insert_one(user).inserted_id)

    # if data['face_image']:
    #     status, face_person_id, face_group_name = face_person_create(user_id, face_id)
    #     if status:
    #         db.user.update_one({'_id': user['_id']}, {'$set': {
    #             'face_person_id': face_person_id,
    #             'face_group_name': face_group_name,
    #         }})

    group = {
        '_id': group_id,
        'name': data['group_name'],
        'password': data['password'],
        'users': {
            user_id: {
                'share_locate': 0,
                'timestamp': now,
                'name': data['user_name'],
                'status': 1,
            }
        },
        'devs': {},
        'timestamp': now,
        'maketime': now_date,
    }
    if data['brief']:
        group['brief'] = data['brief']
    if data['group_email']:
        group['email'] = data['group_email']
    if data['group_image']:
        group['image_id'] = group_image_put(data['group_image'])
    if data['phone']:
        group['users'][user_id]['phone'] = data['phone']
    if 'image_id' in user:
        group['users'][user_id]['image_id'] = user['image_id']

    for i in range(retry_num - 1):
        try:
            db.group.insert_one(group)
            if i != 0:
                db.user.update_one({'_id': user['_id']}, {'$set': {'group_id': group['_id']}})
            break
        except DuplicateKeyError as e:
            if e.code == 11000 and e.details['errmsg'].find('%s.group.$email' % db_name) != -1:
                return failed(E_group_email_conflict)
            group['_id'] = randint(1000000000, 9999999999)
    else:
        if group.get('image_id'):
            group_image_delete(group['image_id'])
        del_session(session_key)
        del_user(user_id)
        return failed(E_cycle_over)
    redis_data = {
        'groups': json.dumps({group['_id']: {'status': 1, 'timestamp': now}}),
    }
    if 'app_ident' in user:
        redis_data['app_ident'] = user['app_ident']
    set_user_session(session_key, user_id, extra=redis_data)

    if data['group_email']:
        gevent.spawn(new_group_mail, data['group_email'], group['_id'], group['password'])
    return succed({
        'group_id': group['_id'],
        'session': session_key,
        'user_id': user_id,
        'user_name': data['user_name'],
        'user_image_url': user_image_normal_path % user['image_id'] if 'image_id' in user else \
            user_image_normal_path_default % user.get('app_ident', 'default')
    })


@validate_decorator(form.GroupNew())  # 新建圈子
def api_group_new(data):
    user_id = data['session_user_id']
    user = db.user.find_one({'_id': ObjectId(user_id)},
                            {'phone': 1, 'share_locate': 1, 'name': 1, 'image_id': 1, 'app_ident': 1, 'type': 1})
    if not user:
        return failed(E_user_nofind)
    now_date = datetime.datetime.now()
    now = time.mktime(now_date.timetuple())
    if not data['group_name']:
        data['group_name'] = generate_group_name(json.loads(
            redis.hget('User:%s' % user_id, 'groups')
        ))
    if not data['password']:
        data['password'] = generate_group_password()

    g_user = {
        'share_locate': user.get('share_locate', 0),
        'timestamp': now,
        'status': 1,
    }
    group = {
        '_id': randint(1000000000, 9999999999),
        'name': data['group_name'],
        'password': data['password'],
        'users': {user_id: g_user},
        'devs': {},
        'timestamp': now,
        'maketime': now_date,
    }
    if data['brief']:
        group['brief'] = data['brief']
    if data['group_email']:
        group['email'] = data['group_email']
    if data['group_image']:
        group['image_id'] = group_image_put(data['group_image'])
    if data['phone']:
        g_user['phone'] = data['phone']
    elif 'phone' in user:
        g_user['phone'] = user['phone']
    if data['user_name']:
        g_user['name'] = data['user_name']
    elif user.get('type') == 2:
        g_user['name'] = generate_user_name()
    else:
        g_user['name'] = user.get('name', generate_user_name())
    if data['user_image']:
        u_image_id = user_image_put(data['user_image'])
        g_user['image_id'] = u_image_id
        user['image_id'] = u_image_id
    elif 'image_id' in user:
        g_user['image_id'] = user.get('image_id')

    for i in range(retry_num):
        try:
            db.group.insert_one(group)
            break
        except DuplicateKeyError as e:
            if e.code == 11000 and e.details['errmsg'].find('%s.group.$email' % db_name) != -1:
                return failed(E_group_email_conflict)
            group['_id'] = randint(1000000000, 9999999999)
        if i == (retry_num - 1):
            if group.get('image_id'):
                group_image_delete(group['image_id'])
            return failed(E_cycle_over)
    old_user_groups = {}
    if add_user_groups(user['_id'], group['_id'], now, old_user_groups=old_user_groups) is None:
        # rollback
        if group['image_id']:
            group_image_delete(group['image_id'])
        db.group.delete_one({'_id': group['_id']})
        return failed(E_server)
    old_group_id = get_user_first_group_id(user_id, old_user_groups)
    if not old_group_id:
        # 用户新建之前没有圈子
        u_update = {
            'name': group['users'][user_id]['name'],
            'group_id': group['_id'],
            'group_name': group['name'],
        }
        if data['user_image']:
            u_update['image_id'] = u_image_id
        if data['identify'] and data['identify'] != user.get('app_ident'):
            u_update['app_ident'] = data['identify']
            redis.hset('User:%s' % user_id, 'app_ident', data['identify'])
            user['app_ident'] = data['identify']
        db.user.update_one({'_id': ObjectId(user_id)}, {'$set': u_update})
        user['app_ident'] = data['identify']
    elif data['identify'] and data['identify'] != user.get('app_ident'):
        db.user.update_one({'_id': ObjectId(user_id)}, {'$set': {'app_ident': data['identify']}})
        redis.hset('User:%s' % user_id, 'app_ident', data['identify'])
        user['app_ident'] = data['identify']
    if data['group_email']:
        gevent.spawn(new_group_mail, data['group_email'], group['_id'], group['password'])
    return succed({
        'group_id': group['_id'],
        'user_image_url': user_image_normal_path % user['image_id'] if 'image_id' in user else \
            user_image_normal_path_default % user.get('app_ident', 'default'),
    })


@validate_decorator(form.GroupModifyUserInfo())  # 修改成员信息
def api_group_modify_user_info(data):
    user_id = data['session_user_id']
    user_groups = redis.hget('User:%s' % user_id, 'groups')
    if not user_groups:
        return failed(E_user_nohas_groups)
    user_groups = json.loads(user_groups)
    group_id = str(data['group_id'])
    if group_id not in user_groups or not user_groups[group_id]['status']:
        return failed(E_user_notin_group)

    group = db.group.find_one({'_id': data['group_id']}, {'users': 1, 'devs': 1, 'contacts': 1})
    try:
        g_users = group.get('users', tuple())
    except AttributeError:
        return failed(E_group_nofind)
    if user_id in g_users:
        g_user = g_users[user_id]
        if not g_user.get('status'):
            return failed(E_user_notin_group)
        if data['phone'] == g_user.get('phone'):
            data['phone'] = None
        if data['user_name'] == g_user.get('name'):
            data['user_name'] = None
    else:
        return failed(E_user_notin_group)

    errno = verify_group_limit(group, data['phone'], data['user_name'], limit_num=False)
    if errno:
        if errno == E_group_name_conflict:
            return failed(E_user_group_name_conflict)
        elif errno == E_group_phone_conflict:
            return failed(E_user_group_phone_conflict)
        else:
            return failed(errno)

    user = db.user.find_one({'_id': ObjectId(user_id)}, {'image_id': 1, 'name': 1, 'app_ident': 1, 'mac': 1})
    g_update = {}
    u_update = {}
    if data['user_name']:
        g_update['users.%s.name' % user_id] = data['user_name']
        u_update['name'] = data['user_name']
    if data['phone']:
        # FIXME 未判断号码,'0000'为保留号码,用于关闭监听指令
        g_update['users.%s.phone' % user_id] = data['phone']
        u_update['phone'] = data['phone']
    if data['share_locate'] is not None:
        if data['share_locate']:
            g_update['users.%s.share_locate' % user_id] = 1
            u_update['share_locate'] = 1
        else:
            g_update['users.%s.share_locate' % user_id] = 0
            u_update['share_locate'] = 0
    if data['user_image']:
        if 'image_id' in user:
            user_image_delete(user['image_id'])
        u_image_id = user_image_put(data['user_image'])
        g_update['users.%s.image_id' % user_id] = u_image_id
        u_update['image_id'] = u_image_id

    if u_update and get_user_first_group_id(user_id, user_groups) == data['group_id']:
        # 同步用户在第一个圈子中的设置的信息
        db.user.update_one({'_id': user['_id']}, {'$set': u_update})

    origin_group_user = group.get('users', {}).get(user_id, {})

    if data['user_image']:
        user_image_id = u_image_id
    elif 'image_id' in origin_group_user or 'image_id' in user:
        user_image_id = str(origin_group_user.get('image_id', user.get('image_id')))
    else:
        user_image_id = None

    if g_update:
        now = time.time()
        g_update['timestamp'] = now
        g_update['users.%s.timestamp' % user_id] = now
        db.group.update_one({'_id': data['group_id']}, {'$set': g_update})

        imei_list = [imei for imei, dev in group.get('devs', {}).items() if dev.get('status')]
        if imei_list:
            gevent.spawn(push_devs_contact_diff, imei_list, {
                'portrait': user_image_small_path % user_image_id if user_image_id else \
                    user_image_small_path_default % user.get('app_ident', 'default'),
                'phone': data['phone'] if data['phone'] else origin_group_user.get('phone', ''),
                'name': data['user_name'] if data['user_name'] else \
                    origin_group_user.get('name', user.get('name', u'未填')),
                'id': user_id,
                'mac': user.get('mac', ''),
                'status': 1,
            })

    return succed({
        'user_image_url': user_image_normal_path % user_image_id if user_image_id else \
            user_image_normal_path_default % user.get('app_ident', 'default'),
    })


@validate_decorator(form.Imei())  # 腕表验证码
def api_watch_get_authcode(data):
    authcode = redis.hget('Watch:%s' % data['imei'], 'authcode')
    if not authcode:
        agent.send_nowait(data['imei'], '\x18', '')
        # 让腕表重新登陆,重新获得加密秘钥
        return failed(E_watch_nocrypt)
    aes = AES.new('%s%s1234' % (data['imei'], authcode))
    auth = ''.join([choice(chars) for _ in range(6)])
    redis.setex('WatchToken:%s:%s' % (data['imei'], auth), 900, 1)
    authtoken = aes.encrypt(auth + ' ' * 10)
    return succed({'crypt_authcode': authtoken.encode('base64')})


@validate_decorator(form.GroupNewWatch())  # 添加腕表
def api_group_new_watch(data):
    user_id = data['session_user_id']
    imei = data['imei']
    user_groups = redis.hget('User:%s' % user_id, 'groups')
    if not user_groups:
        return failed(E_user_nohas_groups)
    user_groups = json.loads(user_groups)
    if str(data['group_id']) not in user_groups or not user_groups[str(data['group_id'])]['status']:
        return failed(E_user_notin_group)

    watch = db.watch.find_one({'_id': imei},
                              {'_id': 1, 'group_id': 1, 'mac': 1, 'name': 1, 'phone': 1, 'image_id': 1, 'status': 1,
                               'fall_status': 1})
    try:
        w_group_id = watch.get('group_id')
    except AttributeError:
        return failed(E_watch_nofind)
    if w_group_id:
        if w_group_id == data['group_id']:
            return failed(E_watch_isin_group)
        else:
            return failed(E_watch_already_has_group)

    if data['authcode'] != '123456' and not redis.get('WatchToken:%s:%s' % (imei, data['authcode'])):
        # FIXME 调试用验证码123456
        return failed(E_watch_auth)

    group = db.group.find_one({'_id': data['group_id']}, {'users': 1, 'devs': 1, 'contacts': 1})
    try:
        g_devs = group.get('devs', tuple())
    except AttributeError:
        return failed(E_group_nofind)

    group_phone, group_names = get_group_phone_name(group)
    if data['phone'] in group_phone:
        return failed(E_watch_group_phone_conflict)
    if data['user_phone'] in group_phone:
        return failed(E_user_group_phone_conflict)
    if data['watch_name'] in group_names:
        return failed(E_watch_group_name_conflict)
    d_update = {
        'group_id': data['group_id'],
        'status': 1,
    }
    if not data['watch_name']:
        if 'name' in watch and watch['name'] not in group_names:
            data['watch_name'] = watch['name']
        else:
            data['watch_name'] = generate_watch_name(group)
    else:
        d_update['name'] = data['watch_name']

    now = time.time()
    g_update = {
        'timestamp': now,
        'devs.%s.operator' % imei: user_id,
        'devs.%s.timestamp' % imei: now,
        'devs.%s.name' % imei: data['watch_name'],
        'devs.%s.status' % imei: 1,
    }
    if data['phone']:
        g_update['devs.%s.phone' % imei] = data['phone']
        d_update['phone'] = data['phone']
    else:
        if imei in g_devs:
            if g_devs[imei].get('phone') in group_phone:
                g_update['devs.%s.phone' % imei] = ''
    if data['user_phone']:
        g_update['users.%s.phone' % user_id] = data['user_phone']
        g_update['users.%s.timestamp' % user_id] = now
        if get_user_first_group_id(user_id, user_groups) == data['group_id']:
            # 同步用户在第一个圈子设置的手机号
            db.user.update_one({'_id': ObjectId(user_id)}, {'$set': {'phone': data['user_phone']}})
    if data['watch_image']:
        w_image_id = watch_image_put(data['watch_image'])
        g_update['devs.%s.image_id' % imei] = w_image_id
        d_update['image_id'] = w_image_id

    db.watch.update_one({'_id': imei}, {'$set': d_update})
    db.group.update_one({'_id': data['group_id']}, {'$set': g_update})
    redis.hmset('Watch:%s' % imei, {
        'group_id': data['group_id'],
        'operator': user_id,
    })

    if watch.get('status', 3) == 2:
        gevent.spawn(interact, imei, '\x14', '')
    agent.send_nowait(imei, '\x08', '')

    if data['watch_image']:
        watch_image_url = watch_image_normal_path % w_image_id
    else:
        watch_image_url = watch_image_normal_path_default % (data['identify'] if data['identify'] else 'default')
    message_id = db.message.insert_one({
        'type': 14,
        'group_id': data['group_id'],
        'imei': imei,
        'sender': user_id,
        'sender_type': 1,
        'timestamp': now,
    }).inserted_id
    push(1, data['group_id'], {
        'push_type': 'talk',
        'group_id': data['group_id'],
        'operator': user_id,
        'imei': imei,
        'mac': watch['mac'],
        'dev_name': data['watch_name'],
        'dev_image_url': watch_image_url,
        'phone': data['phone'] if data['phone'] else watch.get('phone', ''),
        'fast_call_phone': '',
        'lock_status': 0,
        'fall_status': watch.get('fall_status', 0),
        'message_id': str(message_id),
        'type': 14,
        'sender': user_id,
        'sender_type': 1,
        'timestamp': now,
    })
    return succed({
        'dev_image_url': watch_image_url
    })


@validate_decorator(form.SessionGroupId())  # 圈子邀请码
def api_group_generate_invite(data):
    errno = verify_user_in_group(data['session_user_id'], data['group_id'])
    if errno:
        return failed(errno)
    invite_code = redis.get('GroupInvite:%s' % data['group_id'])
    if not invite_code:
        invite_code = randint(100000, 999999)
        redis.setex('GroupInvite:%s' % data['group_id'], 86400, invite_code)
    # else:
    #     redis.expire('GroupInvite:%s' % data['group_id'], 86400)
    return succed({'invitecode': invite_code, 'ttl': 86400})


@validate_decorator(form.GroupAcceptInvite())  # 接收圈子邀请
def api_group_accept_invite(data):
    if data['invitecode'] != redis.get('GroupInvite:%s' % data['group_id']):
        return failed(E_group_auth)
    group = db.group.find_one({'_id': data['group_id']}, {'password': 1})
    try:
        return succed({'group_password': group.get('password', '')})
    except AttributeError:
        return failed(E_group_nofind)


@validate_decorator(form.GroupEnter())  # 进入圈子
def api_group_enter(data):
    if not data['invitecode'] and not data['group_password']:
        return failed(E_params, 'invite code or group password not find')
    if data['group_id'] != 9038491191 and \
            data['invitecode'] and redis.get('GroupInvite:%s' % data['group_id']) != data['invitecode']:
        return failed(E_group_auth)

    user_id = data['session_user_id']
    user_groups, user_has_devicetoken = redis.hmget('User:%s' % user_id, 'groups', 'app_token')
    if user_groups:
        user_group = json.loads(user_groups)
        user_group_id = str(data['group_id'])
        if user_group_id in user_group and user_group[user_group_id].get('status'):
            return failed(E_user_isin_group)

    group = db.group.find_one({'_id': data['group_id']},
                              {'name': 1, 'password': 1, 'timestamp': 1, 'users': 1, 'devs': 1, 'contacts': 1})
    try:
        if data['group_password'] and data['group_password'] != group.get('password') and not data['invitecode']:
            return failed(E_group_password)
    except AttributeError:
        return failed(E_group_nofind)

    errno = verify_group_limit(group, data['phone'], data['user_name'])
    if errno:
        if errno == E_group_name_conflict:
            return failed(E_user_group_name_conflict)
        elif errno == E_group_phone_conflict:
            return failed(E_user_group_phone_conflict)
        else:
            return failed(errno)

    user = db.user.find_one({'_id': ObjectId(user_id)},
                            {'name': 1, 'image_id': 1, 'phone': 1, 'share_locate': 1, 'mac': 1, 'app_ident': 1})
    if not user:
        return failed(E_user_nofind)
    g_user = group.get('users', {}).get(user_id, {})
    now = time.time()

    if data['user_image']:
        u_image_id = user_image_put(data['user_image'])
    else:
        u_image_id = 0

    for u in [g_user, user]:
        if not data['user_name']:
            if 'name' in u:
                errno = verify_group_limit(group, None, u['name'], limit_num=False)
                if not errno:
                    data['user_name'] = u['name']
        if not data['phone']:
            if 'phone' in u:
                errno = verify_group_limit(group, u['phone'], None, limit_num=False)
                if not errno:
                    data['phone'] = u['phone']
        if not u_image_id:
            if 'image_id' in u:
                u_image_id = u['image_id']
    if not data['user_name']:
        # g_user和user中都没有name可用
        data['user_name'] = generate_user_name(group)
    if not data['phone']:
        # g_user和user中都没有phone可用
        data['phone'] = ''
    user_share_locate = g_user.get('share_locate', user.get('share_locate', 0))
    g_update = {
        'timestamp': now,
        'users.%s.name' % user_id: data['user_name'],
        'users.%s.status' % user_id: 1,
        'users.%s.phone' % user_id: data['phone'],
        'users.%s.share_locate' % user_id: user_share_locate,
        'users.%s.timestamp' % user_id: now,
    }
    if u_image_id:
        # 用户上传user_image或从g_user,user处复制image_id
        g_update['users.%s.image_id' % user_id] = u_image_id

    result = db.group.update_one({'_id': data['group_id']}, {'$set': g_update})
    if not result.matched_count:
        return failed(E_group_nofind)

    old_user_groups = {}
    if add_user_groups(user_id, data['group_id'], now, old_user_groups=old_user_groups) is None:
        # rollback
        db.group.update_one({'_id': data['group_id']}, {
            '$unset': {'users.%s' % user_id: 1},
            '$set': {'timestamp': group.get('timestamp', now)}
        })
        return failed(E_server)

    if data['user_image'] and g_user:
        # 若存在旧头像,清空用户上次在圈子中的头像
        if 'image_id' in g_user:
            user_image_delete(g_user['image_id'])

    if user_has_devicetoken:
        redis.sadd('GroupAppleUser:%s' % data['group_id'], user_id)

    old_group_id = get_user_first_group_id(user_id, old_user_groups)
    if not old_group_id:
        # 用户进入之前没有圈子
        u_update = {
            'name': data['user_name'],
            'group_id': data['group_id'],
            'group_name': group['name'],
            'share_locate': user_share_locate,
        }
        if u_image_id:
            u_update['image_id'] = u_image_id
        if data['phone']:
            u_update['phone'] = data['phone']
        if data['identify'] and data['identify'] != user.get('app_ident'):
            u_update['app_ident'] = data['identify']
            redis.hset('User:%s' % user_id, 'app_ident', data['identify'])
            user['app_ident'] = data['identify']
        db.user.update_one({'_id': ObjectId(user_id)}, {'$set': u_update})
        user['app_ident'] = data['identify']
    elif data['identify'] and data['identify'] != user.get('app_ident'):
        db.user.update_one({'_id': ObjectId(user_id)}, {'$set': {'app_ident': data['identify']}})
        redis.hset('User:%s' % user_id, 'app_ident', data['identify'])
        user['app_ident'] = data['identify']

    imei_list = [imei for imei, dev in group.get('devs', {}).items() if dev.get('status')]
    if imei_list:
        gevent.spawn(push_devs_contact_diff, imei_list, {
            'portrait': user_image_small_path % u_image_id if u_image_id else \
                user_image_small_path_default % (
                    data['identify'] if data['identify'] else user.get('app_ident', 'default')),
            'phone': data['phone'] if data['phone'] else '',
            'name': data['user_name'],
            'id': user_id,
            'mac': user.get('mac', ''),
            'status': 1,
        })
    user_image_url = user_image_normal_path % u_image_id if u_image_id else \
        user_image_normal_path_default % user.get('app_ident', 'default')
    message_id = db.message.insert_one({
        'type': 12,
        'group_id': data['group_id'],
        'sender': user_id,
        'sender_type': 1,
        'timestamp': now,
    }).inserted_id
    push(1, data['group_id'], {
        'push_type': 'talk',
        'group_id': data['group_id'],
        'user_id': user_id,
        'user_name': data['user_name'],
        'user_image_url': user_image_url,
        'phone': data['phone'] if data['phone'] else '',
        'share_locate': user_share_locate,
        'message_id': str(message_id),
        'type': 12,
        'sender': user_id,
        'sender_type': 1,
        'timestamp': now,
    })
    return succed({'user_image_url': user_image_url})


@validate_decorator(form.GroupJoin())  # 加入圈子
def api_group_join(data):
    if not data['invitecode'] and not data['group_password']:
        return failed(E_params, 'invite code or group password not find')
    if data['group_id'] != 9038491191 and \
            data['invitecode'] and redis.get('GroupInvite:%s' % data['group_id']) != data['invitecode']:
        return failed(E_group_auth)

    group = db.group.find_one({'_id': data['group_id']},
                              {'_id': 1, 'password': 1, 'timestamp': 1, 'name': 1, 'users': 1, 'devs': 1,
                               'contacts': 1})
    try:
        if data['group_password'] and data['group_password'] != group.get('password', '') and not data['invitecode']:
            return failed(E_group_password)
    except AttributeError:
        return failed(E_group_nofind)

    errno = verify_group_limit(group, data['phone'], data['user_name'])
    if errno:
        if errno == E_group_name_conflict:
            return failed(E_user_group_name_conflict)
        elif errno == E_group_phone_conflict:
            return failed(E_user_group_phone_conflict)
        else:
            return failed(errno)
    if not data['user_name']:
        data['user_name'] = generate_user_name(group)

    now = time.time()
    session_key = generate_session()
    user = {
        'maketime': datetime.datetime.now(),
        'session': session_key,
        'name': data['user_name'],
        'group_id': group['_id'],
        'group_name': group['name'],
        'type': 1,
    }
    if data['user_image']:
        u_image_id = user_image_put(data['user_image'])
        user['image_id'] = u_image_id
    if data['identify']:
        user['app_ident'] = data['identify']
    user_id = db.user.insert_one(user).inserted_id

    # user_id = result.inserted_id

    if 'app_ident' in user:
        set_user_session(session_key, user_id, extra={'app_ident': user['app_ident']})
    else:
        set_user_session(session_key, user_id)

    g_update = {
        'timestamp': now,
        'users.%s.name' % user_id: data['user_name'],
        'users.%s.status' % user_id: 1,
        'users.%s.timestamp' % user_id: now,
    }
    if data['phone']:
        g_update['users.%s.phone' % user_id] = data['phone']
    if 'image_id' in user:
        g_update['users.%s.image_id' % user_id] = user['image_id']
    result = db.group.update_one({'_id': data['group_id']}, {'$set': g_update})
    if not result.matched_count:
        return failed(E_group_nofind)

    if add_user_groups(user_id, data['group_id'], now) is None:
        # rollback
        if 'image_id' in user:
            user_image_delete(user['image_id'])
        db.user.delete_one({'_id': user_id})
        db.group.update_one({'_id': data['group_id']}, {
            '$unset': {'users.%s' % user_id: 1},
            '$set': {'timestamp': group.get('timestamp', now)}
        })
        return failed(E_server)

    user_id = str(user_id)
    imei_list = [imei for imei, dev in group.get('devs', {}).items() if dev.get('status')]
    if imei_list:
        gevent.spawn(push_devs_contact_diff, imei_list, {
            'portrait': user_image_small_path % user['image_id'] if 'image_id' in user else \
                user_image_small_path_default % user.get('app_ident', 'default'),
            'phone': data['phone'] if data['phone'] else '',
            'name': data['user_name'],
            'id': user_id,
            'mac': '',
            'status': 1,
        })
    user_image_url = user_image_normal_path % user['image_id'] if 'image_id' in user else \
        user_image_normal_path_default % user.get('app_ident', 'default')
    message_id = db.message.insert_one({
        'type': 12,
        'group_id': data['group_id'],
        'sender': user_id,
        'sender_type': 1,
        'timestamp': now,
    }).inserted_id
    push(1, data['group_id'], {
        'push_type': 'talk',
        'group_id': data['group_id'],
        'user_id': user_id,
        'user_name': data['user_name'],
        'user_image_url': user_image_url,
        'phone': data['phone'] if data['phone'] else '',
        'share_locate': 0,
        'message_id': str(message_id),
        'type': 12,
        'sender': user_id,
        'sender_type': 1,
        'timestamp': now,
    })
    return succed({
        'session': session_key,
        'user_id': user_id,
        'user_name': data['user_name'],
        'user_image_url': user_image_url
    })


@validate_decorator(form.SessionGroupIdUserId())  # 移出成员
def api_group_remove(data):
    errno = verify_user_in_group(data['session_user_id'], data['group_id'])
    if errno:
        return failed(errno)
    group = db.group.find_one({'_id': data['group_id']}, {'users': 1, 'devs': 1})
    try:
        if not group.get('users'):
            del_group(data['group_id'])
            return failed(E_group_nofind)
    except AttributeError:
        return failed(E_group_nofind)

    remain_users = [u_id for u_id, u in group['users'].items() if u.get('status')]
    if not remain_users:
        del_group(data['group_id'])
        return failed(E_group_nofind)
    if len(remain_users) <= 1:
        return failed(E_group_only_one_user)
    user_id = data['user_id']
    if user_id not in remain_users:
        return failed(E_user_notin_group)
    now = time.time()
    result = db.group.update_one({'_id': data['group_id']}, {'$set': {
        'users.%s.timestamp' % user_id: now,
        'users.%s.status' % user_id: 0,
        'timestamp': now,
    }})
    if not result.modified_count:
        return failed(E_user_notin_group)

    user_data = group['users'].get(data['group_id'])
    old_user_groups = {}
    remain_groups = del_user_groups(user_id, data['group_id'], now, old_user_groups=old_user_groups)
    if remain_groups is None:
        # 事务报错 rollback
        if user_data:
            db.group.update_one({'_id': data['group_id']}, {'$set': {
                'user.%s.timestamp' % user_id: user_data.get('timestamp', now),
                'user.%s.status' % user_id: 1,
            }})
        return failed(E_server)
    elif remain_groups == 'NULL':
        # 删除后用户没有圈子,将用户redis数据下线
        # clean_user_redis(user_id)会导致推送找不到用户token
        # 设置 clean 标志位清除用户redis数据
        redis.hset('User:%s' % user_id, 'clean', 1)
    elif get_user_first_group_id(user_id, old_user_groups) == data['group_id']:
        # 用户的`第一个圈子`变为该用户的其他圈子
        if user_data and 'image_id' in user_data:
            # 删除头像原始数据
            user_image_delete(user_data['image_id'])
        # 将旧数据手动处理,不用再取一次redis
        old_user_groups[str(data['group_id'])]['status'] = 0
        new_top_group_id = get_user_first_group_id(user_id, old_user_groups)
        new_top_group = db.group.find_one({'_id': new_top_group_id}, {'name': 1, 'users': 1})
        if not new_top_group:
            del_user_groups(user_id, new_top_group_id, now)
            return failed(E_user_nohas_groups)
        if user_id in new_top_group.get('users', tuple()):
            n_t_g_user = new_top_group['users'][user_id]
            update = {'$set': {
                'group_id': new_top_group_id,
                'group_name': new_top_group['name'],
                'name': n_t_g_user['name'],
            }, '$unset': {}}
            if 'image_id' in n_t_g_user:
                update['$set']['image_id'] = n_t_g_user['image_id']
            if 'phone' in n_t_g_user:
                update['$set']['phone'] = n_t_g_user['phone']
            else:
                update['$unset']['phone'] = 1
            if 'share_locate' in n_t_g_user:
                update['$set']['share_locate'] = n_t_g_user['share_locate']
            else:
                update['$unset']['share_locate'] = 1
            if not update['$unset']:
                del update['$unset']
            db.user.update_one({'_id': ObjectId(user_id)}, update)
    imei_list = [_ for _, dev in group.get('devs', {}).items() if dev.get('status')]
    if imei_list:
        gevent.spawn(push_devs_contact_diff, imei_list, {
            'portrait': '',
            'phone': '',
            'name': '',
            'id': user_id,
            'mac': '',
            'status': 0,
        })
    message_id = db.message.insert_one({
        'type': 13,
        'group_id': data['group_id'],
        'user_id': user_id,
        'sender': data['session_user_id'],
        'sender_type': 1,
        'timestamp': now,
    }).inserted_id
    if data['session_user_id'] == user_id:
        remain_users.remove(user_id)
    push(3, remain_users, {
        'push_type': 'talk',
        'group_id': data['group_id'],
        'user_id': user_id,
        'operator': data['session_user_id'],
        'message_id': str(message_id),
        'type': 13,
        'sender': data['session_user_id'],
        'sender_type': 1,
        'timestamp': now,
    })
    return succed()


@validate_decorator(form.GroupInfo())  # 圈子详情
def api_group_info(data):
    user_groups, app_ident = redis.hmget('User:%s' % data['session_user_id'], 'groups', 'app_ident')
    if not user_groups:
        return failed(E_user_nohas_groups)
    user_groups = json.loads(user_groups)
    group_id = str(data['group_id'])
    if group_id not in user_groups or not user_groups[group_id]['status']:
        return failed(E_user_notin_group)

    # 根据用户包名判断用户默认头像
    app_ident = app_ident if app_ident else 'default'

    group = db.group.find_one({'_id': data['group_id']})
    if not group:
        return failed(E_group_nofind)
    users = []
    # search_user = []
    for user_id, g_user in group.get('users', {}).items():
        if g_user.get('timestamp') <= data['timestamp']:
            continue
        # status = g_user.get('status', 0)
        # if status:
        #     search_user.append(ObjectId(user_id))
        users.append({
            'user_id': user_id,
            'user_name': g_user.get('name', ''),
            'user_image_url': user_image_normal_path % g_user['image_id'] if 'image_id' in g_user else \
                user_image_normal_path_default % app_ident,
            'phone': g_user.get('phone', ''),
            'status': g_user.get('status', 0),
            'share_locate': g_user.get('share_locate', 0),
            # 'user_timestamp': g_user.get('timestamp', 0),
        })
    # 用户信息在进入圈子时已同步完成,不需要动态查找
    # if search_user:
    #     for user in db.user.find({'_id': {'$in': search_user}}, {'name': 1, 'image_id': 1, 'email': 1}):
    #         user_id = str(user['_id'])
    #         u_users = users[user_id]
    #         if not u_users['user_name']:
    #             u_users['user_name'] = user.get('name', u'未填')
    #         if not u_users['user_image_url']:
    #             u_users['user_image_url'] = user_image_normal_path % u_users.get('image_id', user_default_image_id)
    # 对用户进行排序
    # user_list = users.values()
    # user_list.sort(key=itemgetter('user_timestamp'))
    watchs = {}
    for imei, g_watch in group.get('devs', {}).items():
        if g_watch.get('timestamp') <= data['timestamp']:
            continue
        watchs[imei] = {
            'imei': imei,
            'group_id': group['_id'],
            'dev_name': g_watch.get('name', u'未填'),
            'dev_image_url': watch_image_normal_path % g_watch['image_id'] if 'image_id' in g_watch else \
                watch_image_normal_path_default % app_ident,
            'phone': g_watch.get('phone', ''),
            'fast_call_phone': '',
            'lock_status': 0,
            'fall_status': 0,
            'gps_strategy': '',
            'mac': '',
            'status': g_watch.get('status', 0),
            # 'dev_timestamp': g_watch.get('timestamp', 0),
        }
    search_watch = [imei for imei, watch in watchs.items() if watch['status']]
    if search_watch:
        for watch in db.watch.find({'_id': {'$in': search_watch}}, {
            'status': 1,
            'mac': 1,
            'fall_status': 1,
            'fast_call_phone': 1,
            'gps_strategy': 1
        }):
            g_watch = watchs[watch['_id']]
            g_watch['lock_status'] = 0 if watch.get('status', 2) == 1 else 1
            g_watch['fall_status'] = watch.get('fall_status', 0)
            g_watch['mac'] = watch.get('mac', '')
            g_watch['fast_call_phone'] = watch.get('fast_call_phone', '')
            g_watch['gps_strategy'] = watch.get('gps_strategy', '')
    # dev_list = watchs.values()
    # dev_list.sort(key=itemgetter('dev_timestamp'))
    contacts = []
    for phone, contact in group.get('contacts', {}).items():
        if contact.get('timestamp') <= data['timestamp']:
            continue
        contacts.append({
            'phone': phone,
            'contact_name': contact['name'],
            'contact_image_url': contact_image_normal_path_default % app_ident,
            'status': contact['status'],
            'contact_timestamp': contact['timestamp'],
        })
    contacts.sort(key=itemgetter('contact_timestamp'))
    return succed({
        'group_name': group.get('name', u'未填'),
        'group_email': group.get('email', ''),
        'brief': group.get('brief', u'未填写简介'),
        'password': group.get('password', ''),
        'group_image_url': group_image_normal_path % group['image_id'] if 'image_id' in group else \
            group_image_normal_path_default % app_ident,
        'users': users,
        'devs': watchs.values(),
        # 'users': user_list,
        # 'devs': dev_list,
        'contacts': contacts,
        'group_timestamp': group.get('timestamp', 0)
    })


@validate_decorator(form.SessionTimestamp())  # 用户圈子列表
def api_user_group_list(data):
    user_groups, app_ident = redis.hmget('User:%s' % data['session_user_id'], 'groups', 'app_ident')
    if not user_groups:
        return succed([])
    # 根据用户包名判断用户默认头像
    app_ident = app_ident if app_ident else 'default'
    groups = []
    search_groups = []
    user_groups = json.loads(user_groups)
    for g_id, g_info in user_groups.items():
        if g_info.get('timestamp') > data['timestamp']:
            if g_info.get('status'):
                search_groups.append(int(g_id))
            else:
                groups.append({
                    'group_id': int(g_id),
                    'group_name': '',
                    'group_image_url': '',
                    'status': 0,
                    'timestamp': g_info['timestamp'],
                })
    if search_groups:
        for group in db.group.find({'_id': {'$in': search_groups}}, {'name': 1, 'image_id': 1}):
            groups.append({
                'group_id': group['_id'],
                'group_name': group.get('name', u'未填'),
                'group_image_url': group_image_normal_path % group['image_id'] if 'image_id' in group else \
                    group_image_normal_path_default % app_ident,
                'status': 1,
                'timestamp': user_groups[str(group['_id'])]['timestamp'],
            })
    groups.sort(key=itemgetter('timestamp'))
    return succed(groups)


@validate_decorator(form.GroupAddContact())  # 添加圈子联系人
def api_group_add_contact(data):
    user_groups, app_ident = redis.hmget('User:%s' % data['session_user_id'], 'groups', 'app_ident')
    if not user_groups:
        return failed(E_user_nohas_groups)
    user_groups = json.loads(user_groups)
    group_id = str(data['group_id'])
    if group_id not in user_groups or not user_groups[group_id]['status']:
        return failed(E_user_notin_group)
    app_ident = app_ident if app_ident else 'default'

    group = db.group.find_one({'_id': data['group_id']}, {'users': 1, 'devs': 1, 'contacts': 1})
    if not group:
        return failed(E_group_nofind)
    now = time.time()
    c_update = {
        'timestamp': now,
        'contacts.%s.timestamp' % data['phone']: now,
        'contacts.%s.status' % data['phone']: 1,
    }
    if data['contact_name']:
        errno = verify_group_limit(group, data['phone'], data['contact_name'])
        if errno:
            if errno == E_group_name_conflict:
                return failed(E_contact_group_name_conflict)
            elif errno == E_group_phone_conflict:
                return failed(E_contact_group_phone_conflict)
            else:
                return failed(errno)
        c_update['contacts.%s.name' % data['phone']] = data['contact_name']
    else:
        contact_name = group.get('contacts', {}).get(data['phone'], {}).get('name')
        if not contact_name:
            data['contact_name'] = generate_contact_name(group)
            c_update['contacts.%s.name' % data['phone']] = data['contact_name']
        else:
            data['contact_name'] = contact_name

    result = db.group.update_one({'_id': data['group_id']}, {'$set': c_update})
    if not result.matched_count:
        return failed(E_group_nofind)

    imei_list = [imei for imei, dev in group.get('devs', {}).items() if dev.get('status')]
    if imei_list:
        gevent.spawn(push_devs_contact_diff, imei_list, {
            'portrait': contact_image_small_path_default % app_ident,
            'phone': data['phone'],
            'name': data['contact_name'],
            'id': data['phone'],
            'mac': '',
            'status': 1,
        })
    return succed({
        'contact_name': data['contact_name'],
        'contact_image_url': contact_image_normal_path_default % (data['identify'] if data['identify'] else 'default'),
    })


@validate_decorator(form.GroupDelContact())  # 删除圈子联系人
def api_group_del_contact(data):
    errno = verify_user_in_group(data['session_user_id'], data['group_id'])
    if errno:
        return failed(errno)
    group = db.group.find_one({'_id': data['group_id']}, {'devs': 1, 'contacts': 1})
    try:
        g_contacts = group.get('contacts')
    except AttributeError:
        return failed(E_group_nofind)
    if g_contacts:
        if data['phone'] not in g_contacts:
            return failed(E_group_nocontact)
        if not g_contacts[data['phone']].get('status', 0):
            return failed(E_group_nocontact)
    else:
        return failed(E_group_nocontact)
    now = time.time()
    result = db.group.update_one({'_id': data['group_id']}, {'$set': {
        'timestamp': now,
        'contacts.%s.timestamp' % data['phone']: now,
        'contacts.%s.status' % data['phone']: 0,
    }})
    if not result.matched_count:
        return failed(E_group_nofind)

    imei_list = [imei for imei, dev in group.get('devs', {}).items() if dev.get('status')]
    if imei_list:
        gevent.spawn(push_devs_contact_diff, imei_list, {
            'portrait': '',
            'phone': data['phone'],
            'name': '',
            'id': data['phone'],
            'status': 0,
        })
    return succed()


def push_dev_message(async_result, imei, data):
    if agent.send(imei, '\x0c', data) == OK:
        async_result.set(1)
    else:
        async_result.set(0)


def pack_group_message(m_type, a_length, m_id, s_id, content):
    m_content = content.encode('utf-16-be')
    m_content_length = len(m_content)
    a_length = a_length if a_length else 0
    return pack('>HH12s12sI%ss' % m_content_length,
                m_type, a_length, binascii.a2b_hex(m_id), binascii.a2b_hex(s_id), m_content_length, m_content)


def push_group_message(data, mid, content_url):
    group = db.group.find_one({'_id': data['group_id']}, {'devs': 1})
    if not group:
        del_group(data['group_id'])
    if 'devs' in group:
        pack_data = pack_group_message(data['type'], data['length'], mid, data['session_user_id'],
                                       data['content'] if data['type'] == 3 else content_url)
        pending_list = []
        for imei, g_watch in group['devs'].items():
            if g_watch.get('status'):
                async_result = AsyncResult()
                gevent.spawn(push_dev_message, async_result, imei, pack_data)
                pending_list.append((imei, async_result))
        if pending_list:
            send_message_status = 0
            for imei, r in pending_list:
                ok = r.get()
                if not ok:
                    put_dev_job(imei, '\x0c', pack_data)
                elif not send_message_status:
                    # 继续检查是否有腕表消息需要被放到离线任务,但不需要重复推送圈子消息回执
                    send_message_status = 1
                    push(2, data['session_user_id'], {
                        'push_type': 'talk_status',
                        'group_id': data['group_id'],
                        'message_id': mid,
                        'status': 1,
                        'timestamp': time.time(),
                    })
                    db.message.update_one({'_id': ObjectId(mid)}, {'$set': {'status': 1}})


@validate_decorator(form.GroupSendMessage())  # 发送圈子消息
def api_group_message_send(data):
    errno = verify_user_in_group(data['session_user_id'], data['group_id'])
    if errno:
        return failed(errno)
    timestamp = time.time()
    message = {
        'group_id': data['group_id'],
        'sender': data['session_user_id'],
        'sender_type': 1,
        'type': data['type'],
        'timestamp': timestamp,
        'status': 0,
    }
    if data['type'] == 1:
        if not data['length']:
            return failed(E_params, ('length', 'not find'))
        try:
            audio_data = data['content'].decode('base64')
        except binascii.Error:
            return failed(E_base64_decode)
        content_id = message_audio.put(audio_data)
        content_url = message_audio_path % content_id
        message['content'] = content_id
        message['length'] = data['length']
    elif data['type'] == 2:
        try:
            image_data = data['content'].decode('base64')
        except binascii.Error:
            return failed(E_base64_decode)
        content_id = message_image.put(image_data)
        content_url = message_image_normal_path % content_id
        message['content'] = content_id
    else:
        content_url = ''
        message['content'] = data['content']
    mid = str(db.message.insert_one(message).inserted_id)
    if data['type'] == 1:
        push(1, data['group_id'], {
            'push_type': 'talk',
            'group_id': data['group_id'],
            'sender': data['session_user_id'],
            'sender_type': 1,
            'message_id': mid,
            'type': data['type'],
            'content': data['content'] if data['type'] == 3 else content_url,
            'length': data['length'],
            'timestamp': timestamp
        })
    else:
        push(1, data['group_id'], {
            'push_type': 'talk',
            'group_id': data['group_id'],
            'sender': data['session_user_id'],
            'sender_type': 1,
            'message_id': mid,
            'type': data['type'],
            'content': data['content'] if data['type'] == 3 else content_url,
            'timestamp': timestamp
        })
    gevent.spawn(push_group_message, data, mid, content_url)
    return succed({
        'message_id': mid,
        'content_url': content_url,
    })


@validate_decorator(form.GroupRecvMessage())  # 接收圈子消息
def api_group_message_recv(data):
    errno = verify_user_in_group(data['session_user_id'], data['group_id'])
    if errno:
        return failed(errno)
    sort = -1 if data['sort'] <= 0 else 1
    if data['message_id']:
        try:
            message_id = ObjectId(data['message_id'])
        except InvalidId:
            return failed(E_params, ('message_id', 'unregular ObjectId'))
        result = db.message.find({'group_id': data['group_id'], '_id': {'$lt': message_id}}).sort('_id', sort) \
            .skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.message.find({'group_id': data['group_id']}).sort('_id', sort) \
            .skip(data['page'] * data['num']).limit(data['num'])
    message_list = []
    for message in result:
        if message['type'] == 1:
            message['message_id'] = str(message['_id'])
            del message['_id']
            message['content'] = message_audio_path % message['content']
            message_list.append(message)
        elif message['type'] == 2:
            message['message_id'] = str(message['_id'])
            del message['_id']
            message['content'] = message_image_normal_path % message['content']
            message_list.append(message)
        else:
            message['message_id'] = str(message['_id'])
            del message['_id']
            message_list.append(message)
    return succed(message_list)


@validate_decorator(form.UserBindDeviceToken())  # 绑定deviceToken
def api_user_bind_devicetoken(data):
    if not data.get('session'):
        if data['devicetoken']:
            del_devicetoken(data['devicetoken'])
        return succed()

    devicetoken, ident, version, groups = redis.hmget('User:%s' % data['session_user_id'], 'app_token', 'app_ident',
                                                      'app_version', 'groups')
    if devicetoken == data['devicetoken'] and ident == data['identify'] and version == data['version']:
        return succed()
    if data['devicetoken'] and data['identify'] and data['version']:
        # 重置token数据
        # 删除该token旧数据
        del_devicetoken(data['devicetoken'])
        # 删除用户token旧数据
        if devicetoken:
            db.devicetoken.delete_one({'_id': devicetoken})
        # 更新用户数据
        redis.hmset('User:%s' % data['session_user_id'], {
            'app_ident': data['identify'],
            'app_token': data['devicetoken'],
            'app_version': data['version']
        })
        if groups:
            user_groups = json.loads(groups)
            for group_id, group in user_groups.items():
                if group.get('status'):
                    redis.sadd('GroupAppleUser:%s' % group_id, data['session_user_id'])
        # 更新token数据
        db.devicetoken.update_one({'_id': data['devicetoken']}, {'$set': {'user_id': data['session_user_id']}},
                                  upsert=True)
        db.user.update_one({'_id': ObjectId(data['session_user_id'])}, {'$set': {
            'app_ident': data['identify'],
            'app_token': data['devicetoken'],
            'app_version': data['version'],
        }})
    else:
        del_devicetoken(data['devicetoken'])

    return succed()


@validate_decorator(form.GroupModifyInfo())  # 修改圈子信息
def api_group_modify_info(data):
    # errno = verify_user_in_group(data['session_user_id'], data['group_id'])
    # if errno:
    #     return failed(errno)
    user_groups, app_ident = redis.hmget('User:%s' % data['session_user_id'], 'groups', 'app_ident')
    if not user_groups:
        return failed(E_user_nohas_groups)
    user_groups = json.loads(user_groups)
    group_id = str(data['group_id'])
    if group_id not in user_groups or not user_groups[group_id]['status']:
        return failed(E_user_notin_group)

    # 根据用户包名判断用户默认头像
    app_ident = app_ident if app_ident else 'default'

    group = db.group.find_one({'_id': data['group_id']}, {'name': 1, 'image_id': 1, 'password': 1, 'users': 1})
    g_update = {}
    if data['group_name'] and data['group_name'] != group.get('name'):
        g_update['name'] = data['group_name']
        group['name'] = data['group_name']
        sync_group_info_to_user(group)
    if data['newpassword']:
        g_update['password'] = data['newpassword']
        # 当修改邮箱地址后给发邮件使用
        group['password'] = data['newpassword']
    if data['group_image']:
        if 'image_id' in group:
            group_image_delete(group['image_id'])
        g_image_id = group_image_put(data['group_image'])
        g_update['image_id'] = g_image_id
        group['image_id'] = g_image_id
    if data['group_email']:
        g_update['email'] = data['group_email']
        gevent.spawn(new_group_mail, data['group_email'], group['_id'], group['password'])
    if g_update:
        db.group.update_one({'_id': data['group_id']}, {'$set': g_update})
    return succed({
        'group_image_url': group_image_normal_path % group['image_id'] if 'image_id' in group else \
            group_image_normal_path_default % app_ident,
    })


@validate_decorator(form.SessionGroupId())  # 圈子联系人列表
def api_group_contact_list(data):
    errno = verify_user_in_group(data['session_user_id'], data['group_id'])
    if errno:
        return failed(errno)
    group = db.group.find_one({'_id': data['group_id']}, {'users': 1, 'contacts': 1})
    if not group:
        return failed(E_group_nofind)
    contacts = []
    for user_id in group.get('users', tuple()):
        g_user = group['users'][user_id]
        if g_user.get('status'):
            if 'name' in g_user and 'phone' in g_user:
                contacts.append({
                    'contact_name': g_user['name'],
                    'phone': g_user['phone'],
                    'type': 1,
                })
    for phone in group.get('contacts', tuple()):
        contact = group['contacts'][phone]
        if contact.get('status'):
            contacts.append({
                'contact_name': contact['name'],
                'phone': phone,
                'type': 0,
            })
    return succed(contacts)


# NOTE 使用AsyncResult阻塞对腕表并发的请求,并将结果返回给多个请求
watch_request_poll = {}


@validate_decorator(form.WatchRequestLocate())  # 请求腕表定位
def api_watch_request_locate(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    if data['type'] == 'gps':
        if data['imei'] in watch_request_poll:
            result = watch_request_poll[data['imei']].get()
        else:
            a = AsyncResult()
            watch_request_poll[data['imei']] = a
            result = agent.send(data['imei'], '\x36', '\x02')
            a.set(result)
            del watch_request_poll[data['imei']]
        if result == OK:
            push_user_str = redis.hget('Watch:%s' % data['imei'], 'request_gps_users')
            if push_user_str:
                push_user_list = push_user_str.split(',')
                if data['session_user_id'] not in push_user_list:
                    push_user_list.append(data['session_user_id'])
                    redis.hset('Watch:%s' % data['imei'], 'request_gps_users', ','.join(push_user_list))
            else:
                redis.hset('Watch:%s' % data['imei'], 'request_gps_users', data['session_user_id'])
    else:
        # 请求lbs定位,发送请求腕表持续定位指令
        result = agent.send(data['imei'], '\x0e', '\x00\x06\x00\x0a')
        if result == OK:
            push_user_str = redis.hget('Watch:%s' % data['imei'], 'request_lbs_users')
            if push_user_str:
                push_user_list = push_user_str.split(',')
                if data['session_user_id'] not in push_user_list:
                    push_user_list.append(data['session_user_id'])
                    redis.hset('Watch:%s' % data['imei'], 'request_lbs_users', ','.join(push_user_list))
            else:
                redis.hset('Watch:%s' % data['imei'], 'request_lbs_users', data['session_user_id'])

    if result == OK:
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.SessionImei())  # 结束腕表定位
def api_watch_finish_locate(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    result = agent.send(data['imei'], '\x10', '')
    if result == OK:
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.SessionImei())  # 锁定腕表
def api_watch_locking(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    watch = db.watch.find_one({'_id': data['imei']}, {'status': 1})
    try:
        w_status = watch.get('status', 0)
    except AttributeError:
        return failed(E_watch_nofind)
    if w_status == 2:
        return succed()
    result = agent.send(data['imei'], '\x12', '')
    if result == OK:
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.SessionImei())  # 解锁腕表
def api_watch_unlock(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    watch = db.watch.find_one({'_id': data['imei']}, {'status': 1})
    try:
        w_status = watch.get('status', 0)
    except AttributeError:
        return failed(E_watch_nofind)
    if w_status == 1:
        return succed()
    result = agent.send(data['imei'], '\x14', '')
    if result == OK:
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.SessionImei())  # 监听腕表
def api_watch_monitor(data):
    group_id, monitor_user_id = redis.hmget('Watch:%s' % data['imei'], 'group_id', 'monitor_user_id')
    if not group_id:
        return failed(E_watch_not_has_group)
    user_id = data['session_user_id']
    if monitor_user_id and monitor_user_id != user_id:
        return succed({'monitor_user_id': monitor_user_id})
    group = db.group.find_one({'_id': int(group_id)}, {'users': 1})
    try:
        g_users = group.get('users', tuple())
    except AttributeError:
        return failed(E_group_nofind)
    if user_id not in g_users:
        return failed(E_user_notin_group)
    phone = g_users[user_id].get('phone')
    if not phone:
        return failed(E_user_nohas_phone)
    phone = phone.encode('utf-16-be')
    phone_len = len(phone)
    result = agent.send(data['imei'], '\x16', pack('>I%ss' % phone_len, phone_len, phone))
    if result == OK:
        redis.hset('Watch:%s' % data['imei'], 'monitor_user_id', user_id)
        return succed({'monitor_user_id': user_id})
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.SessionImei())  # 腕表重新登陆
def api_watch_relogin(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    result = agent.send(data['imei'], '\x18', '')
    if result == OK:
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.SessionImei())  # 重启腕表
def api_watch_reboot(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    result = agent.send(data['imei'], '\x1a', '')
    if result == OK:
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.SessionImei())  # 腕表开启飞行模式
def api_watch_fightmode(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    result = agent.send(data['imei'], '\x1c', '')
    if result == OK:
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


def push_watch_alarm(imei, alarm_dict):
    num = len(alarm_dict)
    pack_data = [pack('>H', num)]
    for alarm_id, alarm in alarm_dict.items():
        status = 0 if alarm.get('status') == 'off' else 1
        pattern = 0 if alarm.get('pattern') == 'single' else 1
        cycle = alarm.get('cycle', [1, 2, 3, 4, 5])
        cycle_num = 0
        for c in cycle:
            cycle_num += 2 ** (8 - c)
        cycle_num += pattern
        hour, minute = alarm.get('time', '08:00').split(':')
        h = int(hour)
        m = int(minute)
        label = alarm.get('label', '').encode('utf-16-be')
        l_length = len(label)
        pack_data.append(pack('>BBBBH%ss' % l_length, status, cycle_num, h, m, l_length, label))
    gevent.spawn(interact, imei, '\x1e', ''.join(pack_data))


@validate_decorator(form.WatchAlarmSet())  # 设置腕表闹铃
def api_watch_alarm_set(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    watch = db.watch.find_one({'_id': data['imei']}, {'alarms': 1})

    if data['cycle']:
        new_cycle = list({int(i) for i in data['cycle'].split(',') if 0 < int(i) < 8})
        if len(new_cycle) < 1:
            return failed(E_params, ('cycle', 'has incorrect element'))
        data['cycle'] = new_cycle
    # 闹铃周期
    if data['pattern'] == 'single':
        if not data['cycle']:
            return failed(E_params, ('cycle', 'not cycle but pattern is single'))
        if len(data['cycle']) > 1:
            return failed(E_params, ('cycle', 'too many cycle element but pattern is single'))
    # 闹铃时间
    if data['time']:
        hour, minute = data['time'].split(':')
        if 0 > int(hour) or int(hour) > 23:
            return failed(E_params, ('time', 'hour incorrect'))
        if 0 > int(minute) or int(minute) > 59:
            return failed(E_params, ('time', 'minute incorrect'))
    now = time.time()
    try:
        w_alarms = watch.get('alarms')
    except AttributeError:
        return failed(E_watch_nofind)

    if data['id']:
        # 删除或修改闹钟
        if not w_alarms or data['id'] not in w_alarms:
            return failed(E_watch_alarm_nofind)
        if data['status'] == 'delete':
            db.watch.update_one({'_id': data['imei']}, {'$unset': {'alarms.%s' % data['id']: 1}})
            del w_alarms[data['id']]
            alarm = w_alarms.copy()
            push_watch_alarm(data['imei'], alarm)
        else:
            update = {}
            new_alarm = {}
            if data['status']:
                update['alarms.%s.status' % data['id']] = data['status']
                new_alarm['status'] = data['status']
            if data['cycle']:
                update['alarms.%s.cycle' % data['id']] = data['cycle']
                new_alarm['cycle'] = data['cycle']
            if data['time']:
                update['alarms.%s.time' % data['id']] = data['time']
                new_alarm['time'] = data['time']
            if data['label']:
                update['alarms.%s.label' % data['id']] = data['label']
                new_alarm['label'] = data['label']
            if data['pattern']:
                update['alarms.%s.pattern' % data['id']] = data['pattern']
                new_alarm['pattern'] = data['pattern']
            if update:
                update['alarms.%s.timestamp' % data['id']] = now
                db.watch.update_one({'_id': data['imei']}, {'$set': update})
                alarm = w_alarms.copy()
                for k, v in new_alarm.items():
                    alarm[data['id']][k] = v
                push_watch_alarm(data['imei'], alarm)
        new_id = data['id']
    else:
        # 新建闹钟
        if data['status'] == 'delete':
            return failed(E_params, ('status', 'status is delete but id not exist'))
        if w_alarms:
            for i in range(retry_num):
                new_id = str(randint(100000, 999999))
                if new_id not in w_alarms:
                    break
                if i == (retry_num - 1):
                    return failed(E_cycle_over)
        else:
            new_id = str(randint(100000, 999999))
        new_alarm = {
            'status': data['status'] if data['status'] else 'on',
            'cycle': data['cycle'] if data['cycle'] else [1, 2, 3, 4, 5],
            'time': data['time'] if data['time'] else '08:00',
            'label': data['label'] if data['label'] else u'闹铃',
            'pattern': data['pattern'] if data['pattern'] else 'cycle',
        }
        db.watch.update_one({'_id': data['imei']}, {'$set': {
            'alarms.%s.status' % new_id: new_alarm['status'],
            'alarms.%s.cycle' % new_id: new_alarm['cycle'],
            'alarms.%s.time' % new_id: new_alarm['time'],
            'alarms.%s.label' % new_id: new_alarm['label'],
            'alarms.%s.pattern' % new_id: new_alarm['pattern'],
            'alarms.%s.timestamp' % new_id: now,  # 排序用
        }})
        if w_alarms:
            alarm = w_alarms.copy()
            alarm[new_id] = new_alarm
        else:
            alarm = {new_id: new_alarm}
        push_watch_alarm(data['imei'], alarm)
    return succed({'id': new_id})


@validate_decorator(form.SessionImei())  # 获取腕表闹铃
def api_watch_alarm_get(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    watch = db.watch.find_one({'_id': data['imei']}, {'alarms': 1})
    try:
        w_alarms = watch.get('alarms')
    except AttributeError:
        return failed(E_watch_nofind)
    alarm_list = []
    if w_alarms:
        for alarm_id, alarm in w_alarms.items():
            alarm['id'] = alarm_id
            alarm_list.append(alarm)
        if len(alarm_list) > 1:
            alarm_list.sort(key=itemgetter('timestamp'))
    return succed(alarm_list)


# NOTE 使用CacheBuffer缓存用户的上一个轨迹点
UserLastLocusCache = CacheBuffer(expire=86400)


# NOTE 不能跨进程缓存,对 /v1/user_upload_locate 的请求应该由一个进程单独处理
@validate_decorator(form.UserUploadLocate())  # APP上传定位
def api_user_upload_locate(data):
    if not 180 >= data['lon'] >= -180 or not 90 >= data['lat'] >= -90:
        logger.warning('%s upload bad value, [%s,%s]' % (data['session_user_id'], data['lon'], data['lat']))
        return succed()

    now = time.time()
    db.user_locate.insert_one({
        'user_id': data['session_user_id'],
        'loc': [data['lon'], data['lat']],
        'radius': data['radius'],
        'timestamp': now,
    })
    if data['type'] == 2:
        group_id, push_user_str = redis.hmget('User:%s' % data['session_user_id'], 'group_id', 'map_push_user')
        if push_user_str:
            push_user_list = push_user_str.split(',')
            push(3, push_user_list, {
                'push_type': 'user_locate',
                'user_id': data['session_user_id'],
                'lon': data['lon'],
                'lat': data['lat'],
                'timestamp': now,
            })
            redis.hdel('User:%s' % data['session_user_id'], 'map_push_user')
    # 用户新轨迹点标识
    has_new_locus = 0
    # 当前定位时间
    now_struct_time = time.gmtime(now)
    # 上次定位轨迹缓存
    last_locus_cache = UserLastLocusCache.get(data['session_user_id'])
    if last_locus_cache:
        if last_locus_cache['struct_time'].tm_yday != now_struct_time.tm_yday:
            # 上次的轨迹点日期和这次定位的不同
            has_new_locus = 1
        elif distance(data['lon'], data['lat'], last_locus_cache['lon'], last_locus_cache['lat']) > last_locus_cache[
            'radius']:
            # 距离超过轨迹半径,生成轨迹点
            has_new_locus = 1
    else:
        last_locus = db.user_locus.find_one({'user_id': data['session_user_id']}, sort=[('timestamp', -1)])
        if last_locus:
            last_struct_time = time.gmtime(last_locus['timestamp'])
            if last_struct_time.tm_yday < now_struct_time.tm_yday:
                has_new_locus = 1
            elif distance(data['lon'], data['lat'], last_locus['lon'], last_locus['lat']) > last_locus['radius']:
                # 距离超过轨迹半径,生成轨迹点
                has_new_locus = 1
            else:
                # 没有轨迹点生成,但是将最后一个轨迹点缓存
                UserLastLocusCache[data['session_user_id']] = {
                    'lon': last_locus['lon'],
                    'lat': last_locus['lat'],
                    'struct_time': last_struct_time,
                    'radius': last_locus['radius'],
                }
        else:
            # 还未有过轨迹点
            has_new_locus = 1
    if has_new_locus:
        # 轨迹点间有效半径,200~500以内,看定位的精度
        if data['radius'] > 500:
            locus_radius = 500
        elif data['radius'] < 200:
            locus_radius = 200
        else:
            locus_radius = data['radius']
        UserLastLocusCache[data['session_user_id']] = {
            'lon': data['lon'],
            'lat': data['lat'],
            'struct_time': now_struct_time,
            'radius': locus_radius,
        }
        # 生成轨迹信息
        db.user_locus.insert_one({
            'user_id': data['session_user_id'],
            'lon': data['lon'],
            'lat': data['lat'],
            'radius': locus_radius,
            'timestamp': now,
        })
    return succed()


@validate_decorator(form.SessionGroupIdUserId())  # 查询用户信息
def api_user_info(data):
    group = db.group.find_one({'_id': data['group_id']}, {'users': 1})
    try:
        if data['user_id'] not in group.get('users', tuple()) or not group['users'][data['user_id']].get('status'):
            return failed(E_user_notin_group)
    except AttributeError:
        return failed(E_group_nofind)

    user = db.user.find_one({'_id': ObjectId(data['user_id'])}, {
        'email': 1,
        'phone': 1,
        'image_id': 1,
        'name': 1,
        'app_ident': 1,
    })
    g_user = group['users'][data['user_id']]
    try:
        u_image_id = g_user.get('image_id', user.get('image_id'))
    except AttributeError:
        return failed(E_user_nofind)
    data = {
        'user_id': data['user_id'],
        'user_name': g_user.get('name', user.get('name', u'未填')),
        'user_image_url': user_image_normal_path % u_image_id if u_image_id else \
            user.get('app_ident', 'default'),
        'share_locate': g_user.get('share_locate', 0),
        'phone': g_user.get('phone', user.get('phone', '')),
    }
    return succed(data)


@validate_decorator(form.DelWatch())  # 删除腕表
def api_group_del_watch(data):
    group = db.group.find_one({'_id': data['group_id']}, {'devs': 1})
    imei = data['imei']
    try:
        if imei not in group.get('devs', tuple()) or not group['devs'][imei].get('status'):
            return failed(E_watch_notin_group)
    except AttributeError:
        return failed(E_group_nofind)

    now = time.time()
    db.group.update_one({'_id': data['group_id']}, {'$set': {
        'devs.%s.timestamp' % imei: now,
        'devs.%s.status' % imei: 0,
        'timestamp': now,
    }})
    retain = 0 if data['throughly'] else 1
    del_watch(imei, retain_some_data=retain)
    message_id = db.message.insert_one({
        'type': 15,
        'group_id': data['group_id'],
        'imei': imei,
        'sender': data['session_user_id'],
        'sender_type': 1,
        'timestamp': now,
    }).inserted_id
    push(1, data['group_id'], {
        'push_type': 'talk',
        'group_id': data['group_id'],
        'imei': imei,
        'operator': data['session_user_id'],
        'message_id': str(message_id),
        'type': 15,
        'sender': data['session_user_id'],
        'sender_type': 1,
        'timestamp': now,
    })
    return succed()


@validate_decorator(form.WatchInfo())  # 查询腕表信息
def api_watch_info(data):
    search_key = {
        'status': 1,
        'mac': 1,
        'fall_status': 1,
        'fast_call_phone': 1,
        'gps_strategy': 1,
    }
    if not data['imei'] and not data['mac']:
        return failed(E_params, 'imei or mac not find')
    elif not data['imei'] and data['mac']:
        watch = db.watch.find_one({'mac': data['mac']}, search_key)
        if not watch:
            return failed(E_mac_resolve)
    else:
        watch = None
    group_id = redis.hget('Watch:%s' % data['imei'], 'group_id')
    if not group_id:
        return succed({
            'imei': data['imei'],
            'group_id': 0,
            'dev_name': u'腕表',
            'dev_image_url': '',
            'lock_status': 0,
            'fall_status': 0,
            'phone': '',
            'fast_call_phone': '',
            'gps_strategy': '',
        })

    group = db.group.find_one({'_id': int(group_id)}, {'devs': 1})
    try:
        g_devs = group.get('devs')
    except AttributeError:
        return failed(E_group_nofind)

    if g_devs:
        if data['imei'] not in g_devs or not g_devs[data['imei']].get('status'):
            return failed(E_watch_notin_group)
    else:
        return failed(E_watch_notin_group)

    if not watch:
        watch = db.watch.find_one({'_id': data['imei']}, search_key)
        if not watch:
            return failed(E_watch_nofind)

    g_watch = g_devs[data['imei']]
    return succed({
        'imei': data['imei'],
        'group_id': group['_id'],
        'dev_name': g_watch.get('name', u'未填'),
        'dev_image_url': watch_image_normal_path % g_watch['image_id'] if 'image_id' in g_watch else \
            watch_image_normal_path_default % 'default',
        'lock_status': 0 if watch.get('status', 2) == 1 else 1,
        'fall_status': watch.get('fall_status', 0),
        'phone': g_watch.get('phone', ''),
        'mac': watch.get('mac', ''),
        'fast_call_phone': watch.get('fast_call_phone', ''),
        'gps_strategy': watch.get('gps_strategy', ''),
    })


@validate_decorator(form.GroupModifyWatchInfo())  # 修改腕表信息
def api_group_modify_watch_info(data):
    user_groups, app_ident = redis.hmget('User:%s' % data['session_user_id'], 'groups', 'app_ident')
    if not user_groups:
        return failed(E_user_nohas_groups)
    user_groups = json.loads(user_groups)
    group_id = str(data['group_id'])
    if group_id not in user_groups or not user_groups[group_id]['status']:
        return failed(E_user_notin_group)

    # 根据用户包名判断用户默认头像
    app_ident = app_ident if app_ident else 'default'

    group = db.group.find_one({'_id': data['group_id']}, {'users': 1, 'devs': 1, 'contacts': 1})
    if not group:
        return failed(E_group_nofind)
    imei = data['imei']
    if imei in group.get('devs', tuple()):
        g_watch = group['devs'][imei]
        if not g_watch.get('status'):
            return failed(E_watch_notin_group)
        if data['phone'] == g_watch.get('phone'):
            data['phone'] = None
    else:
        return failed(E_watch_notin_group)

    group_phone_list, group_names_list = get_group_phone_name(group)
    if data['phone']:
        if data['phone'] in group_phone_list:
            return failed(E_watch_group_phone_conflict)
        if len(group_phone_list) >= group_contact_size:
            return failed(E_group_too_much_contact)
    if data['watch_name'] and data['watch_name'] in group_names_list:
        return failed(E_watch_group_name_conflict)

    g_update = {}
    d_update = {}
    if data['fast_call_phone']:
        if data['fast_call_phone'] == 'delete':
            db.watch.update_one({'_id': imei}, {'$unset': {'fast_call_phone': 1}})
            gevent.spawn(interact, imei, '\x26', '\x00\x00\x00\x00')
        elif data['fast_call_phone'] not in group_phone_list:
            return failed(E_phone_notin_group)
        else:
            d_update['fast_call_phone'] = data['fast_call_phone']
            phone = data['fast_call_phone'].encode('utf-16-be')
            phone_len = len(phone)
            gevent.spawn(interact, imei, '\x26', pack('>I%ss' % phone_len, phone_len, phone))
    if data['gps_strategy']:
        if data['gps_strategy'] == 'delete':
            db.watch.update_one({'_id': imei}, {'$unset': {'gps_strategy': 1}})
        else:
            d_update['gps_strategy'] = data['gps_strategy']

    if data['phone']:
        g_update['devs.%s.phone' % imei] = data['phone']
        d_update['phone'] = data['phone']
    if data['watch_name']:
        g_update['devs.%s.name' % imei] = data['watch_name']
        d_update['name'] = data['watch_name']
    if data['watch_image']:
        if 'image_id' in g_watch:
            watch_image_delete(g_watch['image_id'])
        w_image_id = watch_image_put(data['watch_image'])
        g_update['devs.%s.image_id' % imei] = w_image_id
        d_update['image_id'] = w_image_id

    if d_update:
        now = time.time()
        g_update['timestamp'] = now
        db.watch.update_one({'_id': imei}, {'$set': d_update})
        g_update['devs.%s.timestamp' % imei] = now
        db.group.update_one({'_id': data['group_id']}, {'$set': g_update})
        gevent.spawn(interact, imei, '\x02', '')
    return succed({
        'dev_image_url': watch_image_normal_path % w_image_id if data['watch_image'] else \
            watch_image_normal_path_default % app_ident,
    })


@validate_decorator(form.WatchGetLoc())  # 腕表轨迹信息
def api_watch_locus(data):
    find = {'imei': data['imei']}
    if data['type']:
        find['type'] = 1 if data['type'] == 'gps' else 2
    if data['start_timestamp'] and data['end_timestamp']:
        find['timestamp'] = {'$lt': data['end_timestamp'], '$gt': data['start_timestamp']}
        result = db.watch_locus.find(find, {'_id': 0, 'imei': 0}, cursor_type=CursorType.EXHAUST).sort('timestamp', -1)
    elif data['num']:
        result = db.watch_locus.find(find, {'_id': 0, 'imei': 0}).sort('timestamp', -1) \
            .skip(data['page'] * data['num']).limit(data['num'])
    else:
        today_timestamp = time.mktime(datetime.date.today().timetuple())
        find['timestamp'] = {'$gt': today_timestamp}
        result = db.watch_locus.find(find, {'_id': 0, 'imei': 0}, cursor_type=CursorType.EXHAUST).sort('timestamp', -1)
    return succed(list(result))


@validate_decorator(form.WatchGetLocDateNum())  # 腕表轨迹每日数目
def api_watch_locus_datenum(data):
    if not data['start_timestamp']:
        data['start_timestamp'] = time.time() - 7776000  # 90天前
    if not data['end_timestamp']:
        data['end_timestamp'] = time.time()

    result = db.watch_locus.aggregate([
        {'$match': {
            'imei': data['imei'],
            'timestamp': {'$gt': data['start_timestamp'], '$lt': data['end_timestamp']}
        }},
        {'$project': {
            'time': {'$add': [datetime.datetime.min, {"$multiply": [1000, "$timestamp"]}]},
            'timestamp': '$timestamp',
            'type': '$type',
        }},
        {'$group': {
            '_id': {'month': {'$month': '$time'}, 'day': {'$dayOfMonth': '$time'}, 'type': '$type'},
            'timestamp': {'$last': '$timestamp'},
            'sum': {'$sum': 1}
        }}
    ])
    # [{u'_id': {u'day': 17, u'month': 2, "type" : 1}, u'sum': 1, u'timestamp': 1455673732},
    #  {u'_id': {u'day': 28, u'month': 1, "type" : 2}, u'sum': 16, u'timestamp': 1453948750},
    #  {u'_id': {u'day': 25, u'month': 1, "type" : 1}, u'sum': 3, u'timestamp': 1453698330},
    datenum = {}
    for r in result:
        tmp = time.gmtime(r['timestamp'])
        t = calendar.timegm(time.struct_time([tmp.tm_year, tmp.tm_mon, tmp.tm_mday, 0, 0, 0, 0, 0, 0]))
        key = (r['_id']['month'], r['_id']['day'])
        if key in datenum:
            if r['_id']['type'] == 1:
                datenum[key]['gps_num'] = r['sum']
            else:
                datenum[key]['lbs_num'] = r['sum']
        else:
            if r['_id']['type'] == 1:
                datenum[key] = {'timestamp': t, 'lbs_num': 0, 'gps_num': r['sum']}
            else:
                datenum[key] = {'timestamp': t, 'lbs_num': r['sum'], 'gps_num': 0}
    datenum_key = datenum.keys()
    datenum_key.sort(key=itemgetter(0, 1), reverse=True)
    return succed([datenum[k] for k in datenum_key])


@validate_decorator(form.WatchGetLoc())  # 腕表定位信息
def api_watch_locate(data):
    if data['start_timestamp'] and data['end_timestamp']:
        result = db.watch_locate.find({
            'imei': data['imei'],
            'timestamp': {'$lt': data['end_timestamp'], '$gt': data['start_timestamp']}
        }, cursor_type=CursorType.EXHAUST).sort('timestamp', -1)
    elif data['num']:
        result = db.watch_locate.find({'imei': data['imei']}).sort('timestamp', -1).skip(
            data['page'] * data['num']).limit(data['num'])
    else:
        result = db.watch_locate.find({'imei': data['imei']}).sort('timestamp', -1).limit(1)

    locate_list = []
    for locate in result:
        locate_list.append({
            'type': locate['type'],
            'radius': locate['radius'],
            'lon': locate['loc'][0],
            'lat': locate['loc'][1],
            'address': locate.get('address', ''),
            'timestamp': locate['timestamp'],
        })
    return succed(locate_list)


@validate_decorator(form.UserGetLoc())  # 用户轨迹信息
def api_user_locus(data):
    group = db.group.find_one({'_id': data['group_id']}, {'users': 1})
    try:
        if data['user_id'] not in group.get('users', tuple()):
            return failed(E_user_notin_group)
    except AttributeError:
        return failed(E_group_nofind)

    g_user = group['users'][data['user_id']]
    if not g_user.get('status'):
        return failed(E_user_notin_group)
    if g_user.get('share_locate', 0) == 0:
        return failed(E_user_unshare_locate)

    if data['start_timestamp'] and data['end_timestamp']:
        result = db.user_locus.find(
            {'user_id': data['user_id'], 'timestamp': {'$lt': data['end_timestamp'], '$gt': data['start_timestamp']}},
            {'_id': 0, 'user_id': 0}).sort('timestamp', -1)
    elif data['num']:
        result = db.user_locus.find({'user_id': data['user_id']}, {'_id': 0, 'user_id': 0}).sort('timestamp', -1).skip(
            data['page'] * data['num']).limit(data['num'])
    else:
        today_timestamp = time.mktime(datetime.date.today().timetuple())
        result = db.user_locus.find({'user_id': data['user_id'], 'timestamp': {'$gt': today_timestamp}},
                                    {'_id': 0, 'user_id': 0}).sort('timestamp', -1)
    return succed(list(result))


@validate_decorator(form.UserGetLoc())  # 用户定位信息
def api_user_locate(data):
    group = db.group.find_one({'_id': data['group_id']}, {'users': 1})
    try:
        if data['user_id'] not in group.get('users', tuple()):
            return failed(E_user_notin_group)
    except AttributeError:
        return failed(E_group_nofind)

    g_user = group['users'][data['user_id']]
    if not g_user.get('status'):
        return failed(E_user_notin_group)
    if g_user.get('share_locate', 0) == 0:
        return failed(E_user_unshare_locate)

    if data['start_timestamp'] and data['end_timestamp']:
        result = db.user_locate.find(
            {'user_id': data['user_id'],
             'timestamp': {'$lt': data['end_timestamp'], '$gt': data['start_timestamp']}},
            {'loc': 1, 'address': 1, 'timestamp': 1}).sort('timestamp', -1)
    elif data['num']:
        result = db.user_locate.find({'user_id': data['user_id']}, {'loc': 1, 'address': 1, 'timestamp': 1}) \
            .sort('timestamp', -1).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.user_locate.find({'user_id': data['user_id']}, {'loc': 1, 'address': 1, 'timestamp': 1}) \
            .sort('timestamp', -1).limit(1)

    locate_list = []
    for locate in result:
        locate_list.append({
            'lon': locate['loc'][0],
            'lat': locate['loc'][1],
            'type': 1,
            'radius': locate['radius'],
            'address': locate['address'],
            'timestamp': locate['timestamp'],
        })
    return succed(locate_list)


@validate_decorator(form.SessionGroupIdUserId())  # 请求用户定位
def api_user_request_locate(data):
    group = db.group.find_one({'_id': data['group_id']}, {'users': 1})
    try:
        if data['user_id'] not in group.get('users', tuple()):
            return failed(E_user_notin_group)
    except AttributeError:
        return failed(E_group_nofind)

    g_user = group['users'][data['user_id']]
    if not g_user.get('status'):
        return failed(E_user_notin_group)
    if g_user.get('share_locate', 0) == 0:
        return failed(E_user_unshare_locate)

    push_user_str = redis.hget('User:%s' % data['user_id'], 'map_push_user')
    if push_user_str:
        push_user_list = push_user_str.split(',')
        if data['session_user_id'] not in push_user_list:
            push_user_list.append(data['session_user_id'])
            redis.hset('User:%s' % data['user_id'], 'map_push_user', ','.join(push_user_list))
    else:
        redis.hset('User:%s' % data['user_id'], 'map_push_user', data['session_user_id'])

    push(2, data['user_id'], {
        'push_type': 'request_user_locate',
        'group_id': data['group_id'],
        'user_id': data['session_user_id'],
    })
    return succed()


banner_list = get_banner_list()
category_list = get_category_list()
hot_list = get_hot_list()


# @validate_decorator(form.AppstoreIndex())  # FIXME 应用首页未用到identify参数
def api_appstore_index():
    return succed({
        'banner': banner_list,
        'category': category_list,
        'hot': hot_list,
    })


@validate_decorator(form.StoryList())  # 故事列表
def api_story_list(data):
    find = {
        'category_id': 'story',
    }
    if data['story_id']:
        try:
            story_id = ObjectId(data['story_id'])
        except InvalidId:
            return failed(E_params, ('story_id', 'unregular ObjectId'))
        find['_id'] = {'$lt': story_id}
    if data['category_id']:
        find['category_id'] = data['category_id']
    result = db.story.find(find).sort('_id', -1).skip(data['page'] * data['num']).limit(data['num'])
    return succed([{
                       'story_id': str(story['_id']),
                       'story_name': story['title'],
                       'story_category_id': story.get('category_id', ''),
                       'story_brief': story['brief'],
                       'story_image_url': story_image_normal_path % story['image_id'],
                       'story_audio_url': story_audio_path % story['audio_id'],
                   } for story in result])


@validate_decorator(form.StoryHotList())  # 热门故事列表
def api_story_hot_list(data):
    category_hot_list = redis.zrange('HotCategory:%s' % data['category_id'], data['page'] * data['num'],
                                     (data['page'] + 1) * data['num'])
    hot_list_id = [ObjectId(sid) for sid in category_hot_list]
    result = list(db.story.find({'_id': {'$in': hot_list_id}}))
    result.sort(lambda x, y: hot_list_id.index(x['_id']) - hot_list_id.index(y['_id']))
    return succed([{
                       'story_id': str(story['_id']),
                       'story_name': story['title'],
                       'story_category_id': story.get('category_id', ''),
                       'story_brief': story['brief'],
                       'story_image_url': story_image_normal_path % story['image_id'],
                       'story_audio_url': story_audio_path % story['audio_id'],
                   } for story in result])


@validate_decorator(form.StoryId())  # 故事详情
def api_story_detail(data):
    try:
        story_id = ObjectId(data['story_id'])
    except InvalidId:
        return failed(E_params, ('story_id', 'unregular ObjectId'))
    story = db.story.find_one({'_id': story_id})
    if not story:
        return failed(E_story_nofind)
    return succed({
        'story_id': data['story_id'],
        'story_name': story['title'],
        'story_category_id': story.get('category_id', ''),
        'story_brief': story['brief'],
        'story_image_url': story_image_normal_path % story['image_id'],
        'story_audio_url': story_audio_path % story['audio_id'],
        'story_slice_text': story['slice_text'],
        'story_slice_images_url': [story_image_normal_path % i for i in story['images']],
        'story_slice_images_num': story['slice_image'],
        'story_slice_time': story['slice_time'],
    })


@validate_decorator(form.SendStory())  # 发送故事
def api_story_send(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    try:
        story_id = ObjectId(data['story_id'])
    except InvalidId:
        return failed(E_params, ('story_id', 'unregular ObjectId'))
    story = db.story.find_one({'_id': story_id}, {'_id': 1, 'category_id': 1, 'content_id': 1})
    if not story:
        return failed(E_story_nofind)
    content_url = (story_content_path % story['content_id']).encode('utf-16-be')
    content_url_len = len(content_url)
    result = agent.send(data['imei'], '\x20',
                        pack('>12sH%ss' % content_url_len, binascii.a2b_hex(data['story_id']), content_url_len,
                             content_url))
    if result == OK:
        if 'category_id' in story:
            redis.zincrby('HotCategory:%s' % story['category_id'], data['story_id'], 1)
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.PlazaSendMessage())  # 发送广场消息
def api_plaza_post(data):
    # 没有圈子的用户不能发广场
    group_id = get_user_first_group_id(data['session_user_id'])
    if not group_id:
        return failed(E_user_post_limit)
    group = db.group.find_one({'_id': group_id}, {'users': 1})
    try:
        if data['session_user_id'] not in group.get('users', tuple()):
            return failed(E_user_notin_group)
    except AttributeError:
        return failed(E_group_nofind)

    plaza_image_id = []
    if data['images']:
        for image_data in data['images']:
            plaza_image_id.append(plaza_image_put(image_data))
        content = data['content'] if data['content'] else ''
    elif data['content']:
        content = data['content']
    else:
        return failed(E_params, 'content or images is required')
    plaza_post = {
        'user_id': data['session_user_id'],
        'likes': [],
        'like_num': 0,
        'content': content,
        'images': plaza_image_id,
        'comments': [],
        'comment_num': 0,
        'timestamp': time.time()
    }
    post_id = str(db.plaza.insert_one(plaza_post).inserted_id)
    return succed({'post_id': post_id})


@validate_decorator(form.PlazaRecvMessage())  # 接收广场消息
def api_plaza(data):
    if data['post_id']:
        try:
            post_id = ObjectId(data['post_id'])
        except InvalidId:
            return failed(E_params, ('post_id', 'unregular ObjectId'))
        result = db.plaza.find({'_id': {'$lt': post_id}}).sort('_id', -1).skip(data['page'] * data['num']).limit(
            data['num'])
    else:
        result = db.plaza.find({}).sort('_id', -1).skip(data['page'] * data['num']).limit(data['num'])
    post_list = []
    plaza_like_list = []
    plaza_like_dict = {}
    plaza_pendding_user_set = set()
    for m in result:
        m_id = str(m['_id'])
        post = {
            'post_id': m_id,
            'user_id': m['user_id'],
            'lon': m.get('lon', 0),
            'lat': m.get('lat', 0),
            'address': m.get('address', ''),
            'likes': m['likes'],
            'like_num': m['like_num'],
            'liking': 2,
            'comments': m['comments'],
            'comment_num': m['comment_num'],
            'timestamp': m['timestamp'],
            'content': m['content'],
            'images': [plaza_image_path % img for img in m['images']],
        }
        plaza_pendding_user_set.add(m['user_id'])
        for ml in m['likes']:
            plaza_pendding_user_set.add(ml['user_id'])
        for mc in m['comments']:
            plaza_pendding_user_set.add(mc['user_id'])
        if data.get('session'):
            plaza_like_id = '%s-%s' % (m_id, data['session_user_id'])
            plaza_like_list.append(plaza_like_id)
            plaza_like_dict[plaza_like_id] = post
        post_list.append(post)
    if data.get('session'):
        # 获取用户对帖子是否点赞
        result = db.plaza_like.find({'_id': {'$in': plaza_like_list}}, {'_id': 1})
        for p_like in result:
            plaza_like_dict[p_like['_id']]['liking'] = 1
    # 获取每个用户的 user_image_url, user_name, group_id, group_name
    result = db.user.find({'_id': {'$in': [ObjectId(uid) for uid in plaza_pendding_user_set]}}, {
        'image_id': 1,
        'name': 1,
        'group_id': 1,
        'group_name': 1
    })
    users = {str(u['_id']): u for u in result}
    app_ident = data['identify'] if data['identify'] else 'default'
    for post in post_list:
        u_info = users.get(post['user_id'], {})
        post['user_image_url'] = user_image_normal_path % u_info['image_id'] if 'image_id' in u_info else \
            user_image_normal_path_default % app_ident
        post['user_name'] = u_info.get('name', u'未填写')
        post['group_id'] = u_info.get('group_id', 0)
        post['group_name'] = u_info.get('group_name', '')
        for pl in post['likes']:
            u_info = users.get(pl['user_id'], {})
            pl['user_image_url'] = user_image_normal_path % u_info['image_id'] if 'image_id' in u_info else \
                user_image_normal_path_default % app_ident
            pl['user_name'] = u_info.get('name', u'未填写')
            pl['group_id'] = u_info.get('group_id', 0)
            pl['group_name'] = u_info.get('group_name', '')
        for pc in post['comments']:
            u_info = users.get(pc['user_id'], {})
            pc['user_image_url'] = user_image_normal_path % u_info['image_id'] if 'image_id' in u_info else \
                user_image_normal_path_default % app_ident
            pc['user_name'] = u_info.get('name', u'未填写')
            pc['group_id'] = u_info.get('group_id', 0)
            pc['group_name'] = u_info.get('group_name', '')
    return succed(post_list)


@validate_decorator(form.PlazaLike())  # 点赞广场消息
def api_plaza_like(data):
    try:
        post_id = ObjectId(data['post_id'])
    except InvalidId:
        return failed(E_params, ('post_id', 'unregular ObjectId'))
    group_id = get_user_first_group_id(data['session_user_id'])
    if not group_id:
        return failed(E_user_nohas_groups)
    group = db.group.find_one({'_id': group_id}, {'users': 1})
    try:
        if data['session_user_id'] not in group.get('users', tuple()):
            return failed(E_user_notin_group)
    except AttributeError:
        return failed(E_group_nofind)

    if data['liking'] == 1:
        now = time.time()
        like = {
            '_id': '%s-%s' % (data['post_id'], data['session_user_id']),
            'user_id': data['session_user_id'],
            'timestamp': now,
        }
        try:
            db.plaza_like.insert_one(like)
        except DuplicateKeyError:
            logger.warning('user(%s) repeat like post(%s)' % (data['session_user_id'], data['post_id']))
            return succed()
        db.plaza.update_one({'_id': post_id}, {
            '$inc': {'like_num': 1},
            '$push': {
                'likes': {
                    '$each': [like],
                    '$slice': 100,
                    '$sort': {'timestamp': -1},
                }
            }
        })
        return succed()
    else:
        result = db.plaza_like.delete_one({'_id': '%s-%s' % (data['post_id'], data['session_user_id'])})
        if result.deleted_count:
            db.plaza.update_one({'_id': post_id}, {'$inc': {'like_num': -1}, '$pull': {'likes': {
                'user_id': data['session_user_id'],
            }}})
        else:
            logger.warning('user(%s) repeat unlike post(%s)' % (data['session_user_id'], data['post_id']))
        return succed()


@validate_decorator(form.PlazaComment())  # 评论广场消息
def api_plaza_comment(data):
    try:
        post_id = ObjectId(data['post_id'])
    except InvalidId:
        return failed(E_params, ('post_id', 'unregular ObjectId'))
    group_id = get_user_first_group_id(data['session_user_id'])
    if not group_id:
        return failed(E_user_nohas_groups)
    group = db.group.find_one({'_id': group_id}, {'users': 1})
    try:
        if data['session_user_id'] not in group.get('users', tuple()):
            return failed(E_user_notin_group)
    except AttributeError:
        return failed(E_group_nofind)

    now = time.time()
    comment = {
        'post_id': data['post_id'],
        'user_id': data['session_user_id'],
        'content': data['content'],
        'timestamp': now,
    }
    comment['comment_id'] = str(db.plaza_comment.insert_one(comment).inserted_id)
    del comment['_id']
    del comment['post_id']
    result = db.plaza.update_one({'_id': post_id}, {
        '$inc': {'comment_num': 1},
        '$push': {
            'comments': {
                '$each': [comment],
                '$slice': 100,
                '$sort': {'timestamp': -1},
            }
        }
    })
    if not result.matched_count:
        return failed(E_plaza_notfind)

    user = db.user.find_one({'_id': ObjectId(data['session_user_id'])}, {
        'name': 1,
        'image_id': 1,
        'group_id': 1,
        'group_name': 1,
        'app_ident': 1,
    })
    if not user:
        del_session(data['session'])
        return failed(E_session)
    return succed({
        'comment_id': comment['comment_id'],
        'user_name': user.get('name', u'未填写'),
        'user_image_url': user_image_normal_path % user['image_id'] if 'image_id' in user else \
            user_image_normal_path_default % user.get('app_ident', 'default'),
        'group_id': user.get('group_id', 0),
        'group_name': user.get('group_name', ''),
    })


@validate_decorator(form.PlazaLikeRecord())  # 广场消息点赞记录
def api_plaza_like_record(data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['timestamp']:
        result = db.plaza_like.find({
            '_id': {'$regex': '^%s-' % data['post_id']},
            'timestamp': {'$gt': data['timestamp']}
        }).sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.plaza_like.find({'_id': {'$regex': '^%s-' % data['post_id']}}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    like_list = []
    like_pendding_user_set = set()
    for p in result:
        like_pendding_user_set.add(p['user_id'])
        like_list.append({
            'user_id': p['user_id'],
            'timestamp': p['timestamp'],
        })
    result = db.user.find({'_id': {'$in': [ObjectId(uid) for uid in like_pendding_user_set]}}, {
        'image_id': 1,
        'name': 1,
        'group_id': 1,
        'group_name': 1
    })
    app_ident = data['identify'] if data['identify'] else 'default'
    users = {str(u['_id']): u for u in result}
    for like in like_list:
        u_info = users.get(like['user_id'], {})
        like['user_image_url'] = user_image_normal_path % u_info['image_id'] if 'image_id' in u_info else \
            user_image_normal_path_default % app_ident
        like['user_name'] = u_info.get('name', u'未填写')
        like['group_id'] = u_info.get('group_id', 0)
        like['group_name'] = u_info.get('group_name', '')
    return succed(like_list)


@validate_decorator(form.PlazaCommentRecord())  # 广场消息评论记录
def api_plaza_comment_record(data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['comment_id']:
        try:
            comment_id = ObjectId(data['comment_id'])
        except InvalidId:
            return failed(E_params, ('comment_id', 'unregular ObjectId'))
        result = db.plaza_comment.find({'post_id': data['post_id'], '_id': {'$lt': comment_id}}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.plaza_comment.find({'post_id': data['post_id']}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    comment_list = []
    comment_pendding_user_set = set()
    for p in result:
        comment_pendding_user_set.add(p['user_id'])
        comment_list.append({
            'comment_id': str(p['_id']),
            'user_id': p['user_id'],
            'content': p['content'],
            'timestamp': p['timestamp'],
        })
    result = db.user.find({'_id': {'$in': [ObjectId(uid) for uid in comment_pendding_user_set]}}, {
        'image_id': 1,
        'name': 1,
        'group_id': 1,
        'group_name': 1,
    })
    app_ident = data['identify'] if data['identify'] else 'default'
    users = {str(u['_id']): u for u in result}
    for comment in comment_list:
        u_info = users.get(comment['user_id'], {})
        comment['user_image_url'] = user_image_normal_path % u_info['image_id'] if 'image_id' in u_info else \
            user_image_normal_path_default % app_ident
        comment['user_name'] = u_info.get('name', u'未填写')
        comment['group_id'] = u_info.get('group_id', 0)
        comment['group_name'] = u_info.get('group_name', '')
    return succed(comment_list)


@validate_decorator(form.SessionImei())  # 开启腕表脱落告警
def api_watch_falling(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    watch = db.watch.find_one({'_id': data['imei']}, {'fall_status': 1})
    try:
        if watch.get('fall_status', 0) == 1:
            return succed()
    except AttributeError:
        return failed(E_watch_nofind)
    result = agent.send(data['imei'], '\x3a', '')
    if result == OK:
        db.watch.update_one({'_id': data['imei']}, {'$set': {'fall_status': 1}})
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.SessionImei())  # 关闭腕表脱落告警
def api_watch_unfalling(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    watch = db.watch.find_one({'_id': data['imei']}, {'fall_status': 1})
    try:
        if watch.get('fall_status', 0) == 0:
            return succed()
    except AttributeError:
        return failed(E_watch_nofind)
    result = agent.send(data['imei'], '\x3c', '')
    if result == OK:
        db.watch.update_one({'_id': data['imei']}, {'$unset': {'fall_status': 1}})
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.FaceSetSession())  # 上传人脸图像
def api_face_set_session(data):
    user_id = ObjectId(data['session_user_id'])
    user = db.user.find_one({'_id': user_id}, {'face_person_id': 1})
    if not user:
        del_session(data['session'])
        return failed(E_user_nofind)
    status, face = face_upload(data['face_image'])
    if not status:
        return failed(E_face_image_umatch)
    user_face_image_id = user_face.put(data['face_image'])
    if 'face_person_id' not in user:
        status, face_persion_id, face_group_name = face_person_create(data['session_user_id'], face['face_id'])
        if status:
            db.user.update_one({'_id': user_id}, {
                '$set': {
                    'face_person_id': face_persion_id,
                    'face_group_name': face_group_name,
                    'faces': {str(user_face_image_id): face},
                },
                '$push': {
                    'face_images': user_face_image_id,
                }
            })
            return succed()
        else:
            return failed(E_face_person_create)
    else:
        status, result = face_person_adds(user['face_person_id'], face['face_id'])
        if status:
            db.user.update_one({'_id': user_id}, {
                '$set': {
                    'faces.%s' % user_face_image_id: face,
                },
                '$push': {
                    'face_images': user_face_image_id,
                }
            })
            return succed()
        else:
            return failed(E_face_person_adds)


@validate_decorator(form.FaceGetSession())  # 人脸图像获取session
def api_face_get_session(data):
    candidate, group_name = face_identify_person(data['face_id'])
    if not candidate:
        return failed(E_face_nothas_user)
    if candidate['confidence'] < 80:
        condidate_user = db.user.find_one({'_id': ObjectId(candidate['person_name'])}, {'faces': 1})
        try:
            condidate_user_faces = condidate_user.get('faces')
        except AttributeError:
            return failed(E_face_nothas_user)

        if not condidate_user_faces:
            face_person_delete(person_id=candidate['person_id'])
            return failed(E_face_nothas_user)

        for face in condidate_user_faces.values():
            confidence, result = face_compare_face(data['face_id'], face['face_id'])
            if confidence > 90:
                user_id = candidate['person_name']
                person_id = candidate['person_id']
                break
        else:
            return failed(E_face_nothas_user)
    else:
        user_id = candidate['person_name']
        person_id = candidate['person_id']
    user = db.user.find_one({'_id': ObjectId(user_id)}, {'session': 1})
    try:
        return succed({'session': user['session']})
    except TypeError:
        face_person_delete(person_id=person_id)
        return failed(E_face_nothas_user)


@validate_decorator(form.GroupActiveWatch())  # APP预激活腕表
def api_group_active_watch_request(data):
    # 验证 APP、腕表客户号
    # if data['customer_id'] is not None:
    #     errno = verify_identify_customer(data['identify'], data['customer_id'])
    #     if errno:
    #         return failed(errno)

    if not data['session']:
        user_id = ''
    else:
        user_id = data['session_user_id']
    if user_id and data['group_id']:
        errno = verify_user_in_group(user_id, data['group_id'])
        if errno:
            return failed(errno)
    w_group_id = redis.hget('Watch:%s' % data['imei'], 'group_id')
    if w_group_id:
        if int(w_group_id) == data['group_id']:
            return failed(E_watch_isin_group)
        else:
            return failed(E_watch_already_has_group)
    if data['group_id']:
        group = db.group.find_one({'_id': data['group_id']}, {'users': 1, 'devs': 1, 'contacts': 1})
        try:
            if user_id and user_id in group.get('users', tuple()):
                if data['user_phone'] == group['users'][user_id].get('phone'):
                    data['user_phone'] = None
        except AttributeError:
            return failed(E_group_nofind)
    else:
        group = {}
    if group:
        group_phone, group_names = get_group_phone_name(group)
        if data['phone'] and data['user_phone']:
            if data['phone'] in group_phone:
                return failed(E_watch_group_phone_conflict)
            if data['user_phone'] in group_phone:
                return failed(E_user_group_phone_conflict)
            if data['phone'] == data['user_phone']:
                return failed(E_user_watch_phone_same)
        elif data['phone'] and data['phone'] in group_phone:
            return failed(E_watch_group_phone_conflict)
        elif data['user_phone'] and data['user_phone'] in group_phone:
            return failed(E_user_group_phone_conflict)
        if data['watch_name'] in group_names:
            return failed(E_watch_group_name_conflict)
    return succed({
        'user_id': user_id,
        'timestamp': time.time(),
    })


@validate_decorator(form.GroupActiveWatch())  # APP激活腕表
def api_group_active_watch(data):
    user_id = data['session_user_id']
    imei = data['imei']
    user_groups, app_ident = redis.hmget('User:%s' % user_id, 'groups', 'app_ident')
    if not user_groups:
        return failed(E_user_nohas_groups)
    user_groups = json.loads(user_groups)
    if str(data['group_id']) not in user_groups or not user_groups[str(data['group_id'])]['status']:
        return failed(E_user_notin_group)

    app_ident = app_ident if app_ident else 'default'
    if data['identify'] and data['identify'] != app_ident:
        db.user.update_one({'_id': ObjectId(user_id)}, {'$set': {
            'app_ident': data['identify']
        }})
        redis.hset('User:%s' % user_id, 'app_ident', data['identify'])
        app_ident = data['identify']

    # 提前赋值d_update,获得authcode,不用if check_watch两次
    d_update = {
        'group_id': data['group_id'],
        'status': 1,
    }
    check_watch = db.watch.find_one({'_id': imei}, {'group_id': 1, 'authcode': 1, 'maketime': 1})
    if check_watch:
        if 'group_id' in check_watch:
            if check_watch['group_id'] == data['group_id']:
                return failed(E_watch_isin_group)
            else:
                return failed(E_watch_already_has_group)
        if 'authcode' in check_watch:
            # NOTE 将腕表之前的密匙复制过来,避免重复生成密匙
            d_update['authcode'] = check_watch['authcode']
        if 'maketime' in check_watch:
            d_update['maketime'] = check_watch['maketime']

    group = db.group.find_one({'_id': data['group_id']}, {'users': 1, 'devs': 1, 'contacts': 1})
    try:
        if user_id not in group.get('users', tuple()):
            return failed(E_user_notin_group)
    except AttributeError:
        return failed(E_group_nofind)

    g_user = group['users'][user_id]
    if data['user_phone'] == g_user.get('phone'):
        data['user_phone'] = None

    group_phone, group_names = get_group_phone_name(group)
    if data['phone'] and data['user_phone']:
        if data['phone'] in group_phone:
            return failed(E_watch_group_phone_conflict)
        if data['user_phone'] in group_phone:
            return failed(E_user_group_phone_conflict)
        if data['phone'] == data['user_phone']:
            return failed(E_user_watch_phone_same)
    elif data['phone'] and data['phone'] in group_phone:
        return failed(E_watch_group_phone_conflict)
    elif data['user_phone'] and data['user_phone'] in group_phone:
        return failed(E_user_group_phone_conflict)
    if data['watch_name'] in group_names:
        return failed(E_watch_group_name_conflict)
    if not data['watch_name']:
        data['watch_name'] = generate_watch_name(group)
    else:
        d_update['name'] = data['watch_name']

    now = time.time()
    g_update = {
        'timestamp': now,
        'devs.%s.operator' % imei: user_id,
        'devs.%s.timestamp' % imei: now,
        'devs.%s.name' % imei: data['watch_name'],
        'devs.%s.status' % imei: 1,
    }
    if data['phone']:
        g_update['devs.%s.phone' % imei] = data['phone']
        d_update['phone'] = data['phone']
    else:
        if imei in group.get('devs', tuple()):
            if group['devs'][imei].get('phone') in group_phone:
                g_update['devs.%s.phone' % imei] = ''
    if data['user_phone']:
        g_update['users.%s.phone' % user_id] = data['user_phone']
        g_update['users.%s.timestamp' % user_id] = now
        if get_user_first_group_id(user_id, user_groups) == data['group_id']:
            # 同步用户在第一个圈子设置的手机号
            db.user.update_one({'_id': ObjectId(user_id)}, {'$set': {'phone': data['user_phone']}})
        # 推送用户修改的手机号到圈子腕表
        imei_list = [_ for _, dev in group.get('devs', {}).items() if dev.get('status')]
        if imei_list:
            # NOTE 获取用户 mac 地址
            user = db.user.find_one({'_id': ObjectId(user_id)}, {'mac': 1})
            user = user if user else {}
            gevent.spawn(push_devs_contact_diff, imei_list, {
                'portrait': user_image_small_path % g_user['image_id'] if 'image_id' in g_user else \
                    user_image_small_path_default % (data['identify'] if data['identify'] else 'default'),
                'phone': data['user_phone'],
                'name': g_user.get('name', u'未填'),
                'id': user_id,
                'mac': user.get('mac', ''),
                'status': 1,
            })
    if data['watch_image']:
        w_image_id = watch_image_put(data['watch_image'])
        g_update['devs.%s.image_id' % imei] = w_image_id
        d_update['image_id'] = w_image_id
    if data['customer_id']:
        d_update['customer_id'] = data['customer_id']
    if data['mac']:
        d_update['mac'] = data['mac']

    result = db.group.update_one({'_id': data['group_id']}, {'$set': g_update})
    if not result.matched_count:
        return failed(E_group_nofind)

    # 重置腕表对象
    create_watch(imei, update=d_update, now=now)
    redis.hmset('Watch:%s' % imei, {
        'group_id': data['group_id'],
        'operator': user_id,
    })
    agent.send_nowait(imei, '\x08', '')
    watch_image_url = watch_image_normal_path % w_image_id if data['watch_image'] else \
        watch_image_normal_path_default % app_ident
    message_id = db.message.insert_one({
        'type': 14,
        'group_id': data['group_id'],
        'imei': imei,
        'sender': user_id,
        'sender_type': 1,
        'timestamp': now,
    }).inserted_id
    push(1, data['group_id'], {
        'push_type': 'talk',
        'group_id': data['group_id'],
        'operator': user_id,
        'imei': imei,
        'mac': data['mac'],
        'dev_name': data['watch_name'],
        'dev_image_url': watch_image_url,
        'phone': data['phone'] if data['phone'] else '',
        'fast_call_phone': '',
        'lock_status': 0,
        'fall_status': 0,
        'message_id': str(message_id),
        'type': 14,
        'sender': user_id,
        'sender_type': 1,
        'timestamp': now,
    })
    return succed({'dev_image_url': watch_image_url})


@validate_decorator(form.SessionPostId())  # 删除广场消息
def api_plaza_delete(data):
    try:
        post_id = ObjectId(data['post_id'])
    except InvalidId:
        return failed(E_params, ('post_id', 'unregular ObjectId'))
    plaza = db.plaza.find_one({'_id': post_id})
    try:
        if plaza.get('user_id') != data['session_user_id']:
            return failed(E_user_nothas_plaza)
    except AttributeError:
        return failed(E_plaza_notfind)
    if 'images' in plaza:
        for image_id in plaza['images']:
            plaza_image_delete(image_id)
    db.plaza_like.delete_many({'_id': {'$regex': '^%s-' % data['post_id']}})
    db.plaza_comment.delete_many({'post_id': data['post_id']})
    db.plaza.delete_one({'_id': plaza['_id']})
    return succed()


@validate_decorator(form.SessionImei())  # 腕表gps状态信息
def api_watch_gps_info(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    watch_star, catch_star, quality = redis.hmget('Watch:%s' % data['imei'], 'watch_star', 'catch_star', 'star_quality')
    return succed({
        'watch_star': int(watch_star) if watch_star else -1,
        'catch_star': int(catch_star) if catch_star else -1,
        'quality': int(quality) if quality else -1,
    })


@validate_decorator(form.SessionImei())  # 关机腕表
def api_watch_power_off(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    result = agent.send(data['imei'], '\x34', '')
    if result == OK:
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.GroupGenerate())  # 新用户创建圈子并添加腕表
def api_group_generate(data):
    # 验证 APP、腕表客户号
    # if data['customer_id'] is not None:
    #     errno = verify_identify_customer(data['identify'], data['customer_id'])
    #     if errno:
    #         return failed(errno)

    if data['watch_phone'] and data['user_phone'] and data['watch_phone'] == data['user_phone']:
        return failed(E_user_watch_phone_same)
    if data['watch_name'] and data['user_name'] and data['watch_name'] == data['user_name']:
        return failed(E_user_watch_name_same)
    imei = data['imei']
    d_update = {
        'status': 1,
    }
    # 查询腕表是否存在且已经有圈子
    check_watch = db.watch.find_one({'_id': imei}, {'group_id': 1, 'authcode': 1, 'maketime': 1, 'customer_id': 1})
    if check_watch:
        if 'group_id' in check_watch:
            return failed(E_watch_already_has_group)
        if data['authcode']:
            if data['authcode'] != '123456' and not redis.get('WatchToken:%s:%s' % (imei, data['authcode'])):
                # FIXME 调试用验证码123456
                return failed(E_watch_auth, ('authcode', 'authcode incorrect'))
        elif not data['mac']:
            return failed(E_params, ('authcode', 'authcode or mac not exist'))

        if 'authcode' in check_watch:
            # NOTE 将腕表之前的密匙复制过来,避免重复生成密匙
            d_update['authcode'] = check_watch['authcode']
        if 'maketime' in check_watch:
            d_update['maketime'] = check_watch['maketime']
    elif not data['mac']:
        return failed(E_params, ('mac', 'watch and mac do not exist'))

    if not data['watch_name']:
        data['watch_name'] = generate_watch_name()
    else:
        d_update['name'] = data['watch_name']
    if not data['user_name']:
        data['user_name'] = generate_user_name()
    if not data['group_name']:
        data['group_name'] = generate_group_name()
    if not data['password']:
        data['password'] = generate_group_password()
    # 创建用户
    group_id = generate_group_id()
    session_key = generate_session()
    now_date = datetime.datetime.now()
    now = time.mktime(now_date.timetuple())
    user = {
        'maketime': now_date,
        'session': session_key,
        'name': data['user_name'],
        'group_id': group_id,
        'group_name': data['group_name'],
        'type': 1,
    }
    if data['user_image']:
        u_image_id = user_image_put(data['user_image'])
        user['image_id'] = u_image_id
    if data['identify']:
        user['app_ident'] = data['identify']
    # pymongo将insert的 user 自动添加一个_id键, 后面可以使用 user['_id']
    user_id = str(db.user.insert_one(user).inserted_id)

    # 创建圈子
    g_user = {
        'share_locate': 0,
        'timestamp': now,
        'name': data['user_name'],
        'status': 1,
    }
    g_watch = {
        'operator': user_id,
        'timestamp': now,
        'name': data['watch_name'],
        'status': 1,
    }
    group = {
        '_id': group_id,
        'name': data['group_name'],
        'password': data['password'],
        'users': {user_id: g_user},
        'devs': {imei: g_watch},
        'timestamp': now,
        'maketime': now_date,
    }
    if data['brief']:
        group['brief'] = data['brief']
    if data['group_email']:
        group['email'] = data['group_email']
    if data['group_image']:
        group['image_id'] = group_image_put(data['group_image'])
    if data['user_phone']:
        g_user['phone'] = data['user_phone']
    if data['user_image']:
        g_user['image_id'] = u_image_id
    if data['watch_phone']:
        g_watch['phone'] = data['watch_phone']
        d_update['phone'] = data['watch_phone']
    if data['watch_image']:
        w_image_id = watch_image_put(data['watch_image'])
        g_watch['image_id'] = w_image_id
        d_update['image_id'] = w_image_id
    if data['mac']:
        d_update['mac'] = data['mac']

    for i in range(retry_num - 1):
        try:
            db.group.insert_one(group)
            if i != 0:
                db.user.update_one({'_id': user['_id']}, {'$set': {'group_id': group['_id']}})
            break
        except DuplicateKeyError as e:
            if e.code == 11000 and e.details['errmsg'].find('%s.group.$email' % db_name) != -1:
                return failed(E_group_email_conflict)
            group['_id'] = randint(1000000000, 9999999999)
    else:
        if group.get('image_id'):
            group_image_delete(group['image_id'])
        del_session(session_key)
        del_user(user_id)
        return failed(E_cycle_over)

    redis_data = {
        'groups': json.dumps({group['_id']: {'status': 1, 'timestamp': now}}),
    }
    if 'app_ident' in user:
        redis_data['app_ident'] = user['app_ident']
    set_user_session(session_key, user_id, extra=redis_data)

    d_update['group_id'] = group['_id']
    # 重置腕表对象
    create_watch(imei, update=d_update, now=now)
    redis.hmset('Watch:%s' % imei, {
        'group_id': group['_id'],
        'operator': user_id,
    })
    agent.send_nowait(imei, '\x08', '')

    if data['group_email']:
        gevent.spawn(new_group_mail, data['group_email'], group['_id'], group['password'])
    return succed({
        'group_id': group['_id'],
        'session': session_key,
        'user_id': user_id,
        'user_name': data['user_name'],
        'user_image_url': user_image_normal_path % user['image_id'] if 'image_id' in user else \
            user_image_normal_path_default % user.get('app_ident', 'default'),
        'dev_image_url': watch_image_normal_path % w_image_id if data['watch_image'] else \
            watch_image_normal_path_default % user.get('app_ident', 'default'),
    })


@validate_decorator(form.GroupMake())  # 用户创建圈子并添加腕表
def api_group_make(data):
    # 验证 APP、腕表客户号
    # if data['customer_id'] is not None:
    #     errno = verify_identify_customer(data['identify'], data['customer_id'])
    #     if errno:
    #         return failed(errno)

    if data['watch_phone'] and data['watch_phone'] == data['user_phone']:
        return failed(E_user_watch_phone_same)
    if data['watch_name'] and data['watch_name'] == data['user_name']:
        return failed(E_user_watch_name_same)
    imei = data['imei']
    d_update = {
        'status': 1,
    }
    # 查询腕表是否存在且已经有圈子
    check_watch = db.watch.find_one({'_id': imei}, {'group_id': 1, 'authcode': 1, 'maketime': 1})
    if check_watch:
        if 'group_id' in check_watch:
            return failed(E_watch_already_has_group)
        if 'authcode' in check_watch:
            # NOTE 将腕表之前的密匙复制过来,避免重复生成密匙
            d_update['authcode'] = check_watch['authcode']
        if 'maketime' in check_watch:
            d_update['maketime'] = check_watch['maketime']

    user_id = data['session_user_id']
    user = db.user.find_one({'_id': ObjectId(user_id)},
                            {'phone': 1, 'share_locate': 1, 'name': 1, 'image_id': 1, 'app_ident': 1, 'type': 1})
    now_date = datetime.datetime.now()
    now = time.mktime(now_date.timetuple())
    try:
        g_user = {
            'share_locate': user.get('share_locate', 0),
            'timestamp': now,
            'status': 1,
        }
    except AttributeError:
        return failed(E_user_nofind)

    if not data['group_name']:
        data['group_name'] = generate_group_name()
    if not data['password']:
        data['password'] = generate_group_password()
    if not data['watch_name']:
        data['watch_name'] = generate_watch_name()
    else:
        d_update['name'] = data['watch_name']
    if data['user_name']:
        g_user['name'] = data['user_name']
    elif user.get('type') == 2:
        g_user['name'] = generate_user_name()
    else:
        g_user['name'] = user.get('name', generate_user_name())
    if data['user_image']:
        u_image_id = user_image_put(data['user_image'])
        g_user['image_id'] = u_image_id
    elif 'image_id' in user:
        g_user['image_id'] = user.get('image_id')
    if data['user_phone']:
        g_user['phone'] = data['user_phone']

    g_watch = {
        'operator': user_id,
        'timestamp': now,
        'name': data['watch_name'],
        'status': 1,
    }
    # 创建圈子
    group_id = generate_group_id()
    group = {
        '_id': group_id,
        'name': data['group_name'],
        'password': data['password'],
        'users': {user_id: g_user},
        'devs': {imei: g_watch},
        'timestamp': now,
        'maketime': now_date,
    }
    if data['brief']:
        group['brief'] = data['brief']
    if data['group_email']:
        group['email'] = data['group_email']
    if data['group_image']:
        group['image_id'] = group_image_put(data['group_image'])
    if data['watch_phone']:
        g_watch['phone'] = data['watch_phone']
        d_update['phone'] = data['watch_phone']
    if data['watch_image']:
        w_image_id = watch_image_put(data['watch_image'])
        g_watch['image_id'] = w_image_id
        d_update['image_id'] = w_image_id
    if data['mac']:
        d_update['mac'] = data['mac']

    for i in range(retry_num - 1):
        try:
            db.group.insert_one(group)
            break
        except DuplicateKeyError as e:
            if e.code == 11000 and e.details['errmsg'].find('%s.group.$email' % db_name) != -1:
                return failed(E_group_email_conflict)
            group['_id'] = randint(1000000000, 9999999999)
    else:
        if group.get('image_id'):
            group_image_delete(group['image_id'])
        return failed(E_cycle_over)
    # 用户添加圈子信息
    old_user_groups = {}
    if add_user_groups(user_id, group['_id'], now, old_user_groups=old_user_groups) is None:
        # rollback
        if group['image_id']:
            group_image_delete(group['image_id'])
        db.group.delete_one({'_id': group['_id']})
        return failed(E_server)
    old_group_id = get_user_first_group_id(user_id, old_user_groups)
    if not old_group_id:
        # 用户新建之前没有圈子
        u_update = {
            'name': group['users'][user_id]['name'],
            'group_id': group['_id'],
            'group_name': group['name'],
        }
        if data['user_image']:
            u_update['image_id'] = u_image_id
        if data['identify'] and data['identify'] != user.get('app_ident'):
            u_update['app_ident'] = data['identify']
            redis.hset('User:%s' % user_id, 'app_ident', data['identify'])
            user['app_ident'] = data['identify']
        db.user.update_one({'_id': ObjectId(user_id)}, {'$set': u_update})
    elif data['identify'] and data['identify'] != user.get('app_ident'):
        db.user.update_one({'_id': ObjectId(user_id)}, {'$set': {
            'app_ident': data['identify'],
        }})
        redis.hset('User:%s' % user_id, 'app_ident', data['identify'])
        user['app_ident'] = data['identify']

    d_update['group_id'] = group['_id']
    # 新建腕表对象
    create_watch(imei, update=d_update, now=now)
    redis.hmset('Watch:%s' % imei, {
        'group_id': group['_id'],
        'operator': user_id,
    })
    agent.send_nowait(imei, '\x08', '')
    if data['group_email']:
        gevent.spawn(new_group_mail, data['group_email'], group['_id'], group['password'])
    return succed({
        'group_id': group['_id'],
        'user_id': user_id,
        'user_name': data['user_name'],
        'user_image_url': user_image_normal_path % u_image_id if data['user_image'] else \
            user_image_normal_path_default % user.get('app_ident', 'default'),
        'dev_image_url': watch_image_normal_path % w_image_id if data['watch_image'] else \
            watch_image_normal_path_default % user.get('app_ident', 'default'),
    })


@validate_decorator(form.SessionTimestamp())  # 用户圈子腕表列表
def api_user_group_watch_list(data):
    user_groups, app_ident = redis.hmget('User:%s' % data['session_user_id'], 'groups', 'app_ident')
    if not user_groups:
        return succed({'groups': []})
    app_ident = app_ident if app_ident else 'default'
    timestamp = data['timestamp']
    user_groups = json.loads(user_groups)
    user_group_list = []
    search_group_list = []
    for group_id, g in user_groups.items():
        if g.get('status'):
            user_group_list.append(int(group_id))
            search_group_list.append(int(group_id))
        elif g.get('timestamp') > timestamp:
            user_group_list.append(int(group_id))

    groups = {}
    dev_list = []
    for group in db.group.find({'_id': {'$in': search_group_list}}):
        if group.get('timestamp') <= timestamp:
            groups[group['_id']] = None
            continue
        users = [{
                     'user_id': user_id,
                     'user_name': g_user.get('name', ''),
                     'user_image_url': user_image_normal_path % g_user['image_id'] if 'image_id' in g_user else \
                         user_image_normal_path_default % app_ident,
                     'phone': g_user.get('phone', ''),
                     'status': g_user.get('status', 0),
                     'share_locate': g_user.get('share_locate', 0),
                     # 'user_timestamp': g_user.get('timestamp', 0),
                 } for user_id, g_user in group.get('users', {}).items() if g_user.get('timestamp') > timestamp]
        contacts = [{
                        'phone': phone,
                        'contact_name': contact['name'],
                        'contact_image_url': contact_image_normal_path_default % app_ident,
                        'status': contact['status'],
                        'contact_timestamp': contact['timestamp'],
                    } for phone, contact in group.get('contacts', {}).items() if
                    contact.get('timestamp') > timestamp]
        devs = {}
        groups[group['_id']] = {
            'group_id': group['_id'],
            'group_name': group.get('name', u'未填'),
            'group_email': group.get('email', ''),
            'brief': group.get('brief', u'未填写简介'),
            'password': group.get('password', ''),
            'group_image_url': group_image_normal_path % group['image_id'] if 'image_id' in group else \
                group_image_normal_path_default % app_ident,
            'devs': devs,
            'users': users,
            'contacts': contacts,
            'status': user_groups[str(group['_id'])].get('status', 0),
            'group_timestamp': group.get('timestamp', 0),
        }
        for imei, dev in group.get('devs', {}).items():
            if dev.get('timestamp') <= timestamp:
                continue
            if dev.get('status'):
                dev_list.append(imei)
            devs[imei] = {
                'imei': imei,
                'group_id': group['_id'],
                'dev_name': dev.get('name', u'未填'),
                'dev_image_url': watch_image_normal_path % dev['image_id'] if 'image_id' in dev else \
                    watch_image_normal_path_default % app_ident,
                'phone': dev.get('phone', ''),
                'fast_call_phone': '',
                'lock_status': 0,
                'fall_status': 0,
                'gps_strategy': '',
                'mac': '',
                'status': dev.get('status', 0),
            }
    if dev_list:
        for watch in db.watch.find({'_id': {'$in': dev_list}}, {
            'status': 1,
            'mac': 1,
            'fall_status': 1,
            'fast_call_phone': 1,
            'gps_strategy': 1,
            'group_id': 1
        }):
            try:
                dev = groups[watch['group_id']]['devs'][watch['_id']]
                dev['lock_status'] = 0 if watch.get('status', 2) == 1 else 1
                dev['fall_status'] = watch.get('fall_status', 0)
                dev['mac'] = watch.get('mac', '')
                dev['fast_call_phone'] = watch.get('fast_call_phone', '')
                dev['gps_strategy'] = watch.get('gps_strategy', '')
            except KeyError:
                logger.warning('groups: %s, watch: %s' % (repr(groups.keys()), repr(watch)))
                # FIXME 调试
                return failed(E_server)

    if len(groups) != len(user_group_list):
        # 1.数据库中找不到圈子
        # 2.user_group_list有,search_group_list中没有,用户离开该圈子
        for group_id in user_group_list:
            if group_id not in groups:
                groups[group_id] = {
                    'group_id': group_id,
                    'status': 0,
                }

    for gid, g in groups.items():
        try:
            g['devs'] = g['devs'].values()
        except KeyError:
            # 该圈子是用户离开的圈
            pass
        except TypeError:
            # 该圈子时间戳比请求参数小,略过该圈
            del groups[gid]
    return succed({
        'groups': groups.values()
    })


def pack_game_list(title, game_list):
    title = title.encode('utf-16-be')
    game_pack_list = []
    for g in game_list:
        q = g['question'].encode('utf-16-be')
        a = g['answer'].encode('utf-16-be')
        game_pack_list.append(pack('>12sI%ssHI%ss' % (len(q), len(a)),
                                   binascii.a2b_hex(str(g['_id'])),
                                   len(q), q, g['option'], len(a), a
                                   ))
    return pack('>I%ssH' % len(title), len(title), title, len(game_list)) + ''.join(game_pack_list)


def get_game_list(game_id_list):
    game_id_list = [ObjectId(i) for i in game_id_list]
    game_list = []
    for game in db.answer_game.find({'_id': {'$in': game_id_list}}):
        game_list.append(game)
    game_list.sort(key=lambda x: game_id_list.index(x['_id']))
    return game_list


@validate_decorator(form.AnswerGameSend())  # 发送答题游戏
def api_answer_game_send(data):
    errno = verify_user_and_imei(data['session_user_id'], data['imei'])
    if errno:
        return failed(errno)
    answering = redis.hget('Watch:%s' % data['imei'], 'answering')
    if answering:
        return failed(E_watch_answering)
    result = agent.send(data['imei'], '\x44', pack_game_list(u'趣味答题', get_game_list(data['game_id_list'])))
    if result == OK:
        redis.hset('Watch:%s' % data['imei'], 'answering', 1)
        return succed()
    elif result == NO:
        return failed(E_watch_response_offline)
    else:
        return failed(E_watch_response_timeout)


@validate_decorator(form.AnswerGameRank())  # 答题游戏排行榜
def api_answer_game_rank(data):
    rank_search_start = data['page'] * data['num']
    imei_list = redis.zrange('AnswerGame', rank_search_start, (data['page'] + 1) * data['num'])
    watch_list = list(db.watch.find({'_id': {'$in': imei_list}}, {'name': 1, 'image_id': 1,}))
    rank_list = []
    for watch in watch_list:
        rank_list.append({
            'imei': watch['_id'],
            'name': watch.get('name', u'未填写'),
            'image_url': watch_image_normal_path % watch['image_id'] if 'image_id' in watch else \
                watch_image_normal_path_default % (data['identify'] if data['identify'] else 'default'),
            'rank': rank_search_start + 1 + imei_list.index(watch['_id']),
            'score': redis.zscore('AnswerGame', watch['_id']),
        })
    return succed({'rank': rank_list})


@validate_decorator(form.AnswerGameSearch())  # 查询答题游戏排行
def api_answer_game_search(data):
    rank_list = []
    for imei in data['imei_list']:
        rank = redis.zrank('AnswerGame', imei)
        score = redis.zscore('AnswerGame', imei)
        rank_list.append({
            'imei': imei,
            'rank': rank + 1 if rank else 0,
            'score': score if score else 0,
        })
    return succed({'imei_list': rank_list})


game_category_list = get_game_category_list()


# @validate_decorator(form.SessionIdentify())  # FIXME 答题游戏分类列表未用到identify参数
def api_answer_game_category():
    return succed({
        'game_category': game_category_list
    })


@validate_decorator(form.AnswerGameQuestion())  # 获取答题游戏题目
def api_answer_game_question(data):
    return succed({
        'question_list': [
            {
                'question_id': game['_id'],
                'question_content': game['question'],
            } for game in get_random_game_list(data['category_id'], data['num'])]
    })


@validate_decorator(form.AnswerGameList())  # 查询腕表答题列表
def api_watch_answer_game_list(data):
    if data['timestamp']:
        result = db.watch_answer_game.find({'imei': data['imei'], 'end_timestamp': {'$lt': data['timestamp']}}, {
            'num': 1,
            'end_timestamp': 1,
        }).skip(data['page'] * data['num']).limit(data['num']).sort('_id', -1)
    else:
        result = db.watch_answer_game.find({'imei': data['imei']}, {
            'num': 1,
            'end_timestamp': 1,
        }).skip(data['page'] * data['num']).limit(data['num']).sort('_id', -1)
    answer_list = []
    for answer in result:
        answer_list.append({
            'answer_id': str(answer['_id']),
            'num': answer['num'],
            'timestamp': answer['end_timestamp'],
        })
    return succed({'answer_list': answer_list})


@validate_decorator(form.AnswerGame())  # 查询腕表答题结果详情
def api_watch_answer_game(data):
    try:
        answer_id = ObjectId(data['answer_id'])
    except InvalidId:
        return failed(E_params, ('answer_id', 'unregular ObjectId'))
    result = db.watch_answer_game.find_one({'_id': answer_id})
    try:
        question_id_list = [ObjectId(qid) for qid in result['question_list']]
        question = {}
        for Q in db.answer_game.find({'_id': {'$in': question_id_list}}):
            question[str(Q['_id'])] = {
                'question': Q['question'],
                'answer': Q['answer'],
            }
        answer_detail_list = []
        for i, q in enumerate(result['question_list']):
            if q in question:
                Q = question[q]
                answer_detail_list.append({
                    'question_id': q,
                    'question_content': Q['question'],
                    'answer_content': Q['answer'],
                    'result': result['result_list'][i],
                })
        return succed({'answer_detail_list': answer_detail_list})
    except TypeError:
        return succed({'answer_detail_list': []})


@validate_decorator(form.RenewSession())  # 刷新用户session
def api_renew_session(data):
    try:
        user_id = ObjectId(data['user_id'])
    except InvalidId:
        return failed(E_params, ('user_id', 'unregular ObjectId'))
    old_session = redis.hget('User:%s' % user_id, 'session')
    session_key = generate_session()
    result = db.user.update_one({'_id': user_id}, {'$set': {'session': session_key}})
    if result.matched_count:
        set_user_session(session_key, user_id)
        old_user_id = get_session_user_id(old_session)
        if not old_user_id or old_user_id == data['user_id']:
            del_session(old_session)
        return succed({'session': session_key})
    else:
        return failed(E_user_nofind)


@validate_decorator(form.NewUser())  # 新建用户
def api_new_user(data):
    now_date = datetime.datetime.now()
    session_key = generate_session()
    if not data['user_name']:
        data['user_name'] = generate_guest_name()

    user = {
        'maketime': now_date,
        'session': session_key,
        'name': data['user_name'],
        'type': 2,
    }
    if data['user_image']:
        u_image_id = user_image_put(data['user_image'])
        user['image_id'] = u_image_id
    if data['identify']:
        user['app_ident'] = data['identify']

    user_id = str(db.user.insert_one(user).inserted_id)
    redis_data = {}
    if 'app_ident' in user:
        redis_data['app_ident'] = user['app_ident']
    set_user_session(session_key, user_id, extra=redis_data)

    return succed({
        'session': session_key,
        'user_id': user_id,
        'user_name': data['user_name'],
        'user_image_url': user_image_normal_path % user['image_id'] if 'image_id' in user else \
            user_image_normal_path_default % user.get('app_ident', 'default')
    })


@validate_decorator(form.AuthCode())  # 找回用户
def api_resume_user(data):
    auth_key = 'ResumeUser:%s' % data['authcode'].upper()
    with redis.pipeline() as pipe:
        userid = pipe.get(auth_key).delete(auth_key).execute()[0]
    if not userid:
        return failed(E_resume_user_auth)
    try:
        user_id = ObjectId(userid)
    except InvalidId:
        logger.waring('RESUME USER BAD ID %s' % userid)
        return failed(E_resume_user_auth)
    user = db.user.find_one({'_id': user_id})
    if not user:
        return failed(E_user_nofind)
    return succed({
        'session': user['session'],
        'user_id': userid,
        'user_name': user.get('name', ''),
        'user_image_url': user_image_normal_path % user['image_id'] if 'image_id' in user else \
            user_image_normal_path_default % user.get('app_ident', 'default')
    })


medal_list = get_medal_list()


@validate_decorator(form.SessionImei())  # 获取腕表勋章墙
def api_watch_medal_wall(data):
    watch = db.watch.find_one({'_id': data['imei']}, {'medals': 1, 'storys': 1})
    try:
        w_medals = watch.get('medals', [])
        w_storys = watch.get('storys', [])
    except AttributeError:
        return failed(E_watch_nofind)

    walls = []
    for medal in medal_list:
        m = deepcopy(medal)
        m['status'] = 1 if m['medal_id'] in w_medals else 0
        for s in m['goals']:
            s['status'] = 1 if s['story_id'] in w_storys else 0
        walls.append(m)

    return succed({
        'walls': walls
    })


@validate_decorator(form.AnswerMedalQuestion())  # 获取勋章答题题目
def api_answer_medal_question(data):
    return succed({
        'question_list': [
            {
                'question_id': question['_id'],
                'question_content': question['question'],
            } for question in get_medal_question_list(data['medal_id'])]
    })
