# -*- coding: utf-8 -*-
"""
apiv1,apiv2 的通用工具类函数
"""
from __future__ import absolute_import
import gevent
import logging
import time
import requests
import conf
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from gevent.event import Event
from struct import pack
from redis import WatchError
from bson.objectid import ObjectId
from pymongo.cursor import CursorType
from random import randint, choice
from agent.client import Demand, OK
from core.proxy import Client
from core.db import db, redis, dump_pending_task, message_audio, message_image, user_face
from core.tools import restore_user_struct, del_session, clean_user_redis
from static.define import chars
from static.tools import *
from .errno import *

try:
    import ujson as json
except ImportError:
    import json

import sys

if sys.version_info.major < 3:
    range = xrange

logger = logging.getLogger('app')
agent = Demand(conf.agent['host'], conf.agent['request_port'])
push = Client(conf.push['host'], conf.push['port'])

# 圈子联系人个数限制
group_contact_size = 50
# 圈子名字冲突检测最多重试10次,超出限制报 E_cycle_over 错误
retry_num = 10


def generate_session():
    return ''.join([choice(chars) for _ in range(12)])


def get_session_user_id(session_key):
    user_id = redis.hget('Session:%s' % session_key[:3], session_key[3:])
    if not user_id:
        user = db.user.find_one({'session': session_key},
                                {'session': 1, 'app_token': 1, 'app_ident': 1, 'app_version': 1, 'groups': 1})
        if user:
            restore_user_struct(user['_id'], user=user)
            user_id = str(user['_id'])
    return user_id


def add_user_groups(user_id, group_id, now, old_user_groups=None):
    """
    往用户redis数据添加圈子,返回:
        set: {group_id}: 用户现有的所有group_id
        None: None: redis事务冲突
    """
    if not isinstance(group_id, str):
        group_id = str(group_id)
    for i in range(5):
        trans = redis.pipeline()
        trans.watch('User:%s' % user_id)
        groups, devicetoken = redis.hmget('User:%s' % user_id, 'groups', 'app_token')
        if groups:
            groups = json.loads(groups)
            if isinstance(old_user_groups, dict):
                for i, j in groups.items():
                    old_user_groups[i] = j.copy()
            groups[group_id] = {'status': 1, 'timestamp': now}
            new_groups = json.dumps(groups)
            groups = set(g_id for g_id, group in groups.items() if group['status'])
        else:
            new_groups = json.dumps({group_id: {'status': 1, 'timestamp': now}})
            groups = {group_id}
        try:
            trans.multi()
            trans.hset('User:%s' % user_id, 'groups', new_groups)
            trans.execute()

            # 圈子信息写入用户后,如果用户有devicetoken,需同步到圈子
            if devicetoken:
                redis.sadd('GroupAppleUser:%s' % group_id, str(user_id))

            return groups
        except WatchError:
            logger.error('add user groups conflict %s %s' % (user_id, group_id))
            if i == 4:
                return None
            else:
                continue


def del_user_groups(user_id, group_id, now, old_user_groups=None):
    """
    往用户的redis数据删除圈子
    usage:
        result = del_user_groups(user_id, group_id, now, old_user_groups)
        result:
            {group_id1, group_id2}
                # 用户最新的所有group_id
            'NULL'
                # 用户已经没有圈子
            'BADID'
                # 用户没有该圈子
            None
                # redis事务冲突
    """
    for i in range(5):
        group_id = str(group_id)
        trans = redis.pipeline()
        trans.watch('User:%s' % user_id)
        groups = redis.hget('User:%s' % user_id, 'groups')
        if groups:
            groups = json.loads(groups)
            if isinstance(old_user_groups, dict):
                for i, j in groups.items():
                    old_user_groups[i] = j.copy()
            try:
                groups[group_id]['status'] = 0
                groups[group_id]['timestamp'] = now
            except KeyError:
                return 'BADID'
        else:
            return 'NULL'
        try:
            trans.multi()
            trans.hset('User:%s' % user_id, 'groups', json.dumps(groups))
            trans.execute()
            redis.srem('GroupAppleUser:%s' % group_id, user_id)
            remain_groups = set(g_id for g_id, g in groups.items() if g['status'])
            if not remain_groups:
                return 'NULL'
            return remain_groups
        except WatchError:
            logger.error('del user groups conflict %s %s' % (user_id, group_id))
            if i == 4:
                return None
            else:
                continue


def del_user(user_id):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    userid = str(user_id)
    user_groups, devicetoken = redis.hmget('User:%s' % user_id, 'groups', 'app_token')
    if user_groups:
        user_groups = json.loads(user_groups)
        for group_id, user_group in user_groups.items():
            if user_group.get('status'):
                group_id = int(group_id)
                group = db.group.find_one({'_id': group_id}, {'users': 1})
                if not group:
                    redis.delete('GroupAppleUser:%s' % group_id)
                    continue
                for g_user_id in group.get('users', tuple()):
                    if g_user_id == userid:
                        if len(group['users']) == 1:
                            # 圈子中只剩一人,删除圈子
                            del_group(group_id)
                        else:
                            # 在圈子中删除用户
                            if group['users'][g_user_id].get('image_id'):
                                user_image_delete(group['users'][g_user_id]['image_id'])
                            db.group.update_one({'_id': group_id}, {'$set': {
                                'timestamp': time.time(),
                                'users.%s.status' % userid: 0
                            }})
                        if devicetoken:
                            redis.srem('GroupAppleUser:%s' % group_id, userid)
                        break
    user = db.user.find_one({'_id': user_id}, {'session': 1, 'image_id': 1})
    if user:
        if 'image_id' in user:
            user_image_delete(user['image_id'])
        if 'face_images' in user:
            for face_img_id in user['face_images']:
                user_face.delete(face_img_id)
        if 'face_person_id' in user:
            face_person_delete(user['face_person_id'])
        try:
            del_session(user['session'])
        except KeyError:
            pass
        db.user.delete_one({'_id': user_id})
    redis.delete('User:%s' % user_id)


def del_group(group_id):
    if not isinstance(group_id, int):
        group_id = int(group_id)
    group = db.group.find_one({'_id': group_id}, {'users': 1, 'devs': 1})
    if not group:
        return None
    now = time.time()
    for user_id, user in group.get('users', tuple()).items():
        if user.get('status'):
            # NOTE 将 group_id 从 user 列表中删除,防止递归
            result = del_user_groups(user_id, group_id, now)
            if result == 'NULL':
                # NOTE 删除后用户没有圈子,将用户redis数据下线
                clean_user_redis(user_id)
    for imei, watch in group.get('devs', {}).items():
        if watch.get('status'):
            del_watch(imei)
    redis.delete('GroupAppleUser:%s' % group_id)
    db.group.delete_one({'_id': group_id})
    for m in db.message.find({'group_id': group_id, 'type': 1}, cursor_type=CursorType.EXHAUST):
        message_audio.delete(m['content'])
    for m in db.message.find({'group_id': group_id, 'type': 2}, cursor_type=CursorType.EXHAUST):
        message_image.delete(m['content'])
    db.message.delete_many({'group_id': group_id})


def del_watch(imei, retain_some_data=0):
    if not isinstance(imei, str):
        imei = str(imei)
    redis.delete('Watch:%s' % imei)
    redis.zrem('AnswerGame', imei)

    db.watch.delete_one({'_id': imei})
    db.watch_jobbox.delete_many({'imei': imei})
    db.watch_answer_game.delete_many({'imei': imei})
    if not retain_some_data:
        db.watch_locus.delete_many({'imei': imei})
        db.watch_locate.delete_many({'imei': imei})

    agent.send_nowait(imei, '\x0a', '')


def verify_group_limit(group, phone, name, limit_num=True):
    """
    检测圈子:
        1.号码冲突: phone存在时;
        2.名字冲突: name存在时;
        3.联系人与成员数量限制: limit_num为真时;
    usage:
        errno = verify_group_phone_name(group, phone, name)
        if errno:
            return failed(errno)
    """
    group_phone_list = []
    group_names_list = []
    group_user_num = 0
    contacts_phone_list = []
    for uid in group.get('users', tuple()):
        u = group['users'][uid]
        if u.get('status'):
            if 'phone' in u:
                group_phone_list.append(u['phone'])
            if 'name' in u:
                group_names_list.append(u['name'])
            group_user_num += 1
    for imei in group.get('devs', tuple()):
        d = group['devs'][imei]
        if d.get('status'):
            if 'phone' in d:
                group_phone_list.append(d['phone'])
            if 'name' in d:
                group_names_list.append(d['name'])
    for p in group.get('contacts', tuple()):
        contact = group['contacts'][p]
        if contact.get('status'):
            contacts_phone_list.append(p)
            try:
                group_names_list.append(contact['name'])
            except KeyError:
                pass
    if limit_num and (group_user_num + len(contacts_phone_list) >= group_contact_size):
        return E_group_too_much_contact
    if phone and phone in group_phone_list or phone in contacts_phone_list:
        return E_group_phone_conflict
    if name and name in group_names_list:
        return E_group_name_conflict
    return None


def get_group_phone_name(group):
    """
    获取圈子号码,名字列表,用于检测冲突,限制圈子联系人数目
    usage:
        group_phones, group_names = get_group_phone_name(group)
    """
    group_phone = []
    group_names = []
    for uid in group.get('users', tuple()):
        u = group['users'][uid]
        if u.get('status'):
            if 'phone' in u:
                group_phone.append(u['phone'])
            if 'name' in u:
                group_names.append(u['name'])
    for imei in group.get('devs', tuple()):
        d = group['devs'][imei]
        if d.get('status'):
            if 'phone' in d:
                group_phone.append(d['phone'])
            if 'name' in d:
                group_names.append(d['name'])
    for p in group.get('contacts', tuple()):
        contact = group['contacts'][p]
        if contact.get('status'):
            group_phone.append(p)
            try:
                group_names.append(contact['name'])
            except KeyError:
                pass
    return group_phone, group_names


def generate_group_id():
    return randint(1000000000, 9999999999)


def generate_group_password():
    return str(randint(10000, 99999))


def generate_group_name(user_group=None):
    """
    usage:
        group_name = generate_group_name(group)
    """
    if not user_group:
        return u'圈子1'
    return u'圈子%d' % (len([g for g in user_group.values() if g.get('status')]) + 1)


def generate_user_name(group=None):
    """
    usage:
        user_name = generate_user_name(group)
    """
    if not group:
        return u'APP用户1'
    _, group_names = get_group_phone_name(group)
    num = len([u for u in group.get('users', {}).values() if u.get('status')]) + 1
    user_name = u'APP用户%d' % num
    while num < 1000:
        if user_name in group_names:
            num += 1
            user_name = u'APP用户%d' % num
        else:
            return user_name
    return u'APP用户'


def generate_watch_name(group=None):
    """
    usage:
        watch_name = generate_watch_name(group)
    """
    if not group:
        return u'手表用户01'
    _, group_names = get_group_phone_name(group)
    num = len([d for d in group.get('devs', {}).values() if d.get('status')]) + 1
    dev_name = u'手表用户%d' % num
    while num < 1000:
        if dev_name in group_names:
            num += 1
            dev_name = u'手表用户%d' % num
        else:
            return dev_name
    return u'手表用户'


def generate_contact_name(group=None):
    """
    usage:
        contact_name = generate_contact_name(group)
    """
    if not group:
        return u'通讯录用户1'
    _, group_names = get_group_phone_name(group)
    num = len([d for d in group.get('contacts', {}).values() if d.get('status')]) + 1
    contact_name = u'通讯录用户%d' % num
    while num < 1000:
        if contact_name in group_names:
            num += 1
            contact_name = u'通讯录用户%d' % num
        else:
            return contact_name
    return u'通讯录用户'


def generate_guest_name():
    """
    usage:
        guest_name = generate_guest_name()
    """
    return u'游客%06d' % randint(0, 999999)


def get_user_first_group_id(user_id, user_groups=None):
    """
    usage:
        group_id = get_user_first_group_id(user_id)
        # group_id = get_user_first_group_id(user_id, user_groups)
        if not group_id:
            return failed(XXX)
    """
    if not user_groups:
        user_groups = redis.hget('User:%s' % user_id, 'groups')
        if not user_groups:
            return None
        user_groups = json.loads(user_groups)
    elif not isinstance(user_groups, dict):
        user_groups = json.loads(user_groups)
    if not user_groups:
        return None
    effect_user_groups = {gid: g for gid, g in user_groups.items() if g.get('status')}
    if not effect_user_groups:
        return None
    group_id = min(user_groups, key=lambda k: user_groups[k].get('timestamp', 0))
    return int(group_id)


def verify_user_in_group(user_id, group_id, user_groups=None):
    """
    usage:
        errno = verify_user_in_group(user_id, group_id)
        # errno = verify_user_in_group(user_id, group_id, user_groups)
        if errno:
            return failed(errno)
    """
    if not user_groups:
        user_groups = redis.hget('User:%s' % user_id, 'groups')
        if not user_groups:
            return E_user_nohas_groups
        user_groups = json.loads(user_groups)
    elif not isinstance(user_groups, dict):
        user_groups = json.loads(user_groups)
    group_id = str(group_id)
    if group_id not in user_groups or not user_groups[group_id]['status']:
        return E_user_notin_group
    return None


def verify_user_and_imei(user_id, imei):
    """
    usage:
        errno = verify_user_and_imei(user, imei)
        if errno:
            return failed(errno)
    """
    # TODO 验证用户与请求腕表的权限
    return None


def sync_group_info_to_user(group=None):
    """
    usage:
        errno = sync_group_user_info(group_id)
        if errno:
            return failed(errno)
    """
    if not group:
        group = db.group.find_one({'_id': group['_id']}, {'name': 1, 'users': 1})
        if not group:
            return E_group_nofind
    user_id_list = [ObjectId(user_id) for user_id, u in group.get('users', tuple()).items() if u.get('status')]
    if not user_id_list:
        del_group(group['_id'])
        return None
    update_user_id = []
    for user_id in user_id_list:
        if get_user_first_group_id(user_id) == group['_id']:
            update_user_id.append(user_id)
    if update_user_id:
        db.user.update_many({'_id': {'$in': update_user_id}}, {'$set': {
            'group_name': group['name'],
        }})


def push_devs_contact_diff(imei_list, d):
    data = json.dumps(d).encode('utf-16-be')
    l = len(data)
    data = pack('>I%ss' % l, l, data)
    for imei in imei_list:
        if agent.send(imei, '\x06', data) != OK:
            put_dev_job(imei, '\x06', data)


def interact(imei, instruct, data):
    if agent.send(imei, instruct, data) != OK:
        put_dev_job(imei, instruct, data)


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), './new_group.html'), 'r') as f:
    group_html = f.read()


def new_group_mail(email, group_id, group_password):
    struct_now = time.localtime()
    str_now = u'%04d年%02d月%02d日' % (struct_now.tm_year, struct_now.tm_mon, struct_now.tm_mday)
    send_mail(email, '创建家庭圈', group_html % (
        group_id,
        group_password.encode('utf-8'),
        str_now.encode('utf-8'),
    ))


def send_mail(recver, topic, content):
    try:
        msg = MIMEMultipart()
        msg['From'] = 'xxx 团队<admin@xxx.com>'
        msg['To'] = recver
        msg['Subject'] = topic
        txt = MIMEText(content, 'html')
        msg.attach(txt)
        # image = MIMEImage(image_data)
        # image.add_header('Content-ID', '<image1>')
        # msg.attach(image)
        data = msg.as_string()
        smtp = smtplib.SMTP()
        # smtp.set_debuglevel(1)
        smtp.connect('mail.xxx.com', 25)
        smtp.ehlo()
        # smtp.starttls()
        smtp.login('username', 'password')
        smtp.sendmail(
            'admin@xxx.com',
            recver,
            data
        )
    except:
        logger.error('send mail error to <%s>' % recver, exc_info=True)


face_request = requests.Session()
face_key = 'face++ key !'
face_secret = 'face++ secret !'


def face_upload(image_data):
    """
    usage:
        status, face = face_upload(image_data)
        if not status:
            return failed(XXX)
    """
    files = {'img': ('upload.jpg', image_data)}
    face_data = {
        'api_key': face_key,
        'api_secret': face_secret,
        'mode': 'oneface',
        'attribute': 'gender,age,race,smiling,glass,pose',
        'async': 'false',
    }
    result = face_request.post('http://apicn.faceplusplus.com/v2/detection/detect', data=face_data, files=files)
    data = result.json()
    face_num = len(data['face'])
    return face_num, data['face'][0]


def face_person_create(user_id, face_id):
    """
    usage:
        status, person_id, group_name = face_upload(image_data)
        if not status:
            return failed(XXX)
    status:
        创建是否成功
    person_id:
        创建后的person_id,person_name为用户_id
    group_name:
        创建后加入的group_name
    """
    # FIXME User group需要提前创建,10000限制,失败后需重试
    face_data = {
        'api_key': face_key,
        'api_secret': face_secret,
        'person_name': user_id,
        'face_id': face_id,
        'group_name': 'User'
    }
    result = face_request.post('http://apicn.faceplusplus.com/v2/person/create', data=face_data)
    data = result.json()
    if data['added_face'] == 1 and data['added_group'] == 1:
        face_group_need_train('User')
        return True, data['person_id'], 'User'
    logger.error('face_person_create, %s' % repr(data))
    return None, None, None


def face_person_delete(person_id=None, person_name=None):
    """
    usage:
        status, data = face_person_delete(person_id, person_name)
        if not status:
            return failed(XXX)
    """
    face_data = {
        'api_key': face_key,
        'api_secret': face_secret,
    }
    if person_name:
        face_data['person_name'] = person_name
    elif person_id:
        face_data['person_id'] = person_id
    else:
        return None, None
    result = face_request.post('http://apicn.faceplusplus.com/v2/person/delete', data=face_data)
    data = result.json()
    if data.get('deleted') == 1:
        face_group_need_train('User')
        return True, data
    logger.error('face_person_delete failed, %s' % repr(data))
    return None, data


def face_person_adds(person_id, face_id):
    """
    usage:
        status, data = face_person_adds(person_id, face_id)
        if not status:
            return failed(XXX)
    """
    face_data = {
        'api_key': face_key,
        'api_secret': face_secret,
        'person_id': person_id,
        'face_id': face_id,
    }
    result = face_request.post('http://apicn.faceplusplus.com/v2/person/add_face', data=face_data)
    data = result.json()
    if data.get('added') == 1:
        face_group_need_train('User')
        return True, data
    logger.error('face_person_adds, %s' % repr(data))
    return False, data


def face_compare_face(face_id1, face_id2):
    """
    usage:
        confidence, data = face_compare_face(face_id1, face_id2)
        if not confidence:
            return failed(XXX)
    """
    face_data = {
        'api_key': face_key,
        'api_secret': face_secret,
        'face_id1': face_id1,
        'face_id2': face_id2,
    }
    result = face_request.post('http://apicn.faceplusplus.com/v2/recognition/compare', data=face_data)
    data = result.json()
    return data['similarity'], data


def face_identify_person(face_id):
    """
    usage:
        candidate, group_name = face_identify_person(face_id)
        if not user_id:
            return failed(XXX)
    candidate:
        该图像匹配到的最佳candidate
    group_name:
        该图像所在的group_name
    """
    # FIXME 有多个group的时候需要遍历
    face_data = {
        'api_key': face_key,
        'api_secret': face_secret,
        'group_name': 'User',
        'mode': 'oneface',
        'key_face_id': face_id,
        'async': 'false',
    }
    result = face_request.post('http://apicn.faceplusplus.com/v2/recognition/identify', data=face_data)
    data = result.json()
    candidate_num = len(data['face'][0]['candidate'])
    if candidate_num:
        candidate = max(data['face'][0]['candidate'], key=lambda x: x['confidence'])
        return candidate, 'User'
    return None, None, None


def face_group_remove_person(group_name, person_id=None, person_name=None):
    """
    usage:
        status = face_group_remove_person(group_name, person_id)
        if not status:
            return failed(XXX)
    """
    face_data = {
        'api_key': face_key,
        'api_secret': face_secret,
        'group_name': group_name,
    }
    if person_id:
        face_data['person_id'] = person_id
    elif person_name:
        face_data['person_name'] = person_name
    else:
        return False
    result = face_request.post('http://apicn.faceplusplus.com/v2/group/remove_person', data=face_data)
    data = result.json()
    if data['removed'] > 0:
        return True
    logger.error('face_group_remove_person, %s' % repr(data))
    return False


def face_get_result(session_id):
    """
    usage:
        status, result = face_get_result(session_id)
        if not status:
            return failed(XXX)
    """
    face_data = {
        'api_key': face_key,
        'api_secret': face_secret,
        'session_id': session_id,
    }
    result = face_request.post('http://apicn.faceplusplus.com/v2/info/get_session', data=face_data)
    data = result.json()
    return data['status'] == 'SUCC', data['result']


def face_train_group_request(group_id=None, group_name=None):
    """
    usage:
        session_id = face_train_group_request(group_id)
        if not session_id:
            return failed(XXX)
    """
    face_data = {
        'api_key': face_key,
        'api_secret': face_secret,
    }
    if group_id:
        face_data['group_id'] = group_id
    elif group_name:
        face_data['group_name'] = group_name
    else:
        return None
    result = face_request.post('http://apicn.faceplusplus.com/v2/train/identify', data=face_data)
    data = result.json()
    return data['session_id']


def face_group_need_train(group_name):
    face_group_train_set.add(group_name)
    face_group_train_event.set()


face_group_train_set = set()
face_group_train_dict = {}
face_group_train_event = Event()


def face_train_group(group_name=None):
    """
    usage:
        status, result = face_train_group(group_id)
        if not status:
            return failed(XXX)
    """
    if group_name in face_group_train_dict:
        # 还有group任务正在执行
        return None, None
    face_group_train_dict[group_name] = True
    face_group_train_set.discard(group_name)
    try:
        session_id = face_train_group_request(group_name=group_name)
        for i in range(30):
            gevent.sleep(60)
            status, result = face_get_result(session_id)
            if status:
                return status, result
            logging.warn('group %s stil training,session_id %s' % (group_name, session_id))
        else:
            return None, None
    finally:
        del face_group_train_dict[group_name]
        if group_name in face_group_train_set:
            gevent.spawn(face_train_group, group_name)


def face_train_group_task():
    while 1:
        face_group_train_event.wait()
        face_group_train_event.clear()
        if face_group_train_set:
            for group_name in list(face_group_train_set):
                gevent.spawn(face_train_group, group_name)


gevent.spawn(face_train_group_task)


def del_devicetoken(token):
    token = db.devicetoken.find_one({'_id': token})
    if token:
        result = redis.hdel('User:%s' % token['user_id'], 'app_token', 'app_version')
        if result > 0:
            fresh_token_groups = redis.hget('User:%s' % token['user_id'], 'groups')
            if fresh_token_groups:
                user_groups = json.loads(fresh_token_groups)
                for group_id, group in user_groups.items():
                    if group.get('status'):
                        redis.srem('GroupAppleUser:%s' % group_id, token['user_id'])
        db.user.update_one({'_id': ObjectId(token['user_id'])}, {'$unset': {
            'app_token': 1,
            'app_version': 1,
        }})
