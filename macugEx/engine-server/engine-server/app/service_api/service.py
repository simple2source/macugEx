# -*- coding: utf-8 -*-
"""
客服模块的app模块
接口编码过程中,data为表单类处理过的字典,所有字段至少都有值
从mongodb取出的数据字典不可信任,要用get方法获取字典数据
"""
from __future__ import absolute_import
from flask import request, Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from functools import wraps
from werkzeug.wrappers import Response
from bson.objectid import ObjectId, InvalidId
from pymongo.cursor import CursorType
from time import time

try:
    import ujson as json
except ImportError:
    import json

from core.db import db, Q_message_image
from app.api.errno import *
from app.api.tools import get_session_user_id, push, logger
from static.define import *
from . import form
from .errno import *

app = Blueprint('service', __name__, template_folder='templates')


def respond(data):
    r = Response(headers=[('Content-Type', 'application/json')])
    r.data = json.dumps(data)
    return r


def validate_decorator(validator):
    def decorator(func):
        @wraps(func)
        def request_wrapper(*args, **kwargs):
            if request.method == 'POST':
                request_data = request.json if request.mimetype == 'application/json' else request.form if \
                    request.form else json.loads(request.data) if request.data else {}
            else:
                request_data = request.args
            status, data = validator.validate(request_data)
            if status:
                if 'session' in data:
                    user_id = get_session_user_id(data['session'])
                    if not user_id:
                        return respond({'status': 300, 'error': E_session, 'field': 'session'})
                    data['session_user_id'] = user_id
                kwargs['data'] = data
                return func(*args, **kwargs)
            else:
                field, message = data
                return respond({'status': 300, 'error': E_params, 'field': field, 'debug': message})

        return request_wrapper

    return decorator


@app.route('/serv/bind', methods=['POST'])  # 客服登陆(绑定APP)
@validate_decorator(form.ServBind())
def serv_bind(data):
    service = db.service.find_one({'_id': data['serv_id']}, {'password': 1})
    if not service:
        return respond({'status': 300, 'error': E_serv_nofind})
    if data['password'] != service['password']:
        return respond({'status': 300, 'error': E_bad_serv_passwd})
    db.service.update_one({'_id': data['serv_id']}, {'$set': {'user_id': data['session_user_id']}})
    return respond({'status': 200})


@app.route('/question/new', methods=['POST'])  # 客户提问问题
@validate_decorator(form.QuestionNew())
def question_new(data):
    now = time()
    result = db.question.insert_one({
        'user_id': data['session_user_id'],
        'title': data['title'] if data['title'] else '',
        'status': 1,
        'timestamp': now,
    })
    return respond({'status': 200, 'question_id': str(result.inserted_id)})


@app.route('/question/list', methods=['GET'])  # 获取'待解决'用户问题列表
@validate_decorator(form.QuestionList())
def question_list(data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['question_id']:
        try:
            q_id = ObjectId(data['question_id'])
        except InvalidId:
            return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
        result = db.question.find({'_id': {'$lt': q_id}, 'status': 1}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.question.find({'status': 1}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    questions = []
    question_ids = []
    users = {}
    for question in result:
        users[question['user_id']] = {}
        q_id = str(question['_id'])
        question_ids.append(q_id)
        questions.append({
            'question_id': q_id,
            'user_id': question['user_id'],
            'title': question['title'],
            'timestamp': question['timestamp'],
            'status': question['status'],
        })
    for user in db.user.find({'_id': {'$in': [ObjectId(uid) for uid in users.keys()]}}, {'name': 1, 'image_id': 1}):
        users[str(user['_id'])] = {
            'name': user.get('name', u'未填'),
            'image_id': user.get('image_id'),
        }

    last_questions = {}
    for last_question in db.question_message.aggregate([
        {
            '$match': {'question_id': {'$in': question_ids}, 'type': {'$in': [1, 2, 3]}}
        },
        {
            '$sort': {'_id': 1}
        },
        {
            '$group': {
                '_id': '$question_id',
                'timestamp': {'$last': '$timestamp'},
                'sender': {'$last': '$sender'},
                'sender_type': {'$last': '$sender_type'},
                'text': {'$last': '$text'},
                'type': {'$last': '$type'},
            }
        }
    ]):
        last_questions[last_question['_id']] = {
            'timestamp': last_question['timestamp'],
            'sender': last_question['sender'],
            'sender_type': last_question['sender_type'],
            'text': last_question['text'],
            'type': last_question['type'],
        }

    identify = data['identify'] if data['identify'] else 'default'
    for question in questions:
        try:
            user = users[question['user_id']]
            question['user_name'] = user.get('name', u'未填')
            question['user_image_url'] = user_image_normal_path % user['image_id'] if user['image_id'] else \
                user_image_normal_path_default % identify
        except KeyError:
            question['user_name'] = u'未填'
            question['user_image_url'] = user_image_normal_path_default % identify

        try:
            last_question = last_questions[question['question_id']]
            question['last_mess_timestamp'] = last_question['timestamp']
            question['last_mess_sender'] = last_question['sender']
            question['last_mess_sender_type'] = last_question['sender_type']
            if last_question['type'] == 3:
                question['last_mess_text'] = last_question['text']
            elif last_question['type'] == 2:
                question['last_mess_text'] = u'[图片]'
            else:
                question['last_mess_text'] = u'[语音]'
        except:
            question['last_mess_text'] = ''
            question['last_mess_timestamp'] = question['timestamp']
            question['last_mess_sender'] = question['user_id']
            question['last_mess_sender_type'] = 1

    return respond({
        'status': 200,
        'questions': questions,
    })


@app.route('/question/<question_id>/serve', methods=['POST'])  # 开始回答用户问题
@validate_decorator(form.ServId())
def question_serve(question_id, data):
    try:
        q_id = ObjectId(question_id)
    except InvalidId:
        return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
    question = db.question.find_one({'_id': q_id}, {'status': 1, 'user_id': 1})
    if not question:
        return respond({'status': 300, 'error': E_quest_nofind})
    status = question.get('status')
    if status == 1:
        now = time()
        message_id = db.question_message.insert_one({
            'question_id': question_id,
            'type': 4,
            'action': 1,
            'sender': data['serv_id'],
            'sender_type': 2,
            'timestamp': now,
        }).inserted_id
        push(2, question['user_id'], {
            'push_type': 'service',
            'question_id': question_id,
            'message_id': str(message_id),
            'type': 4,
            'action': 1,
            'sender': data['serv_id'],
            'sender_type': 2,
            'timestamp': now,
        })
        db.question.update_one({'_id': q_id}, {'$set': {'status': 2, 'serv_id': data['serv_id']}})
        return respond({'status': 200})
    elif status == 2:
        return respond({'status': 300, 'error': E_quest_inflight})
    else:
        return respond({'status': 300, 'error': E_quest_finish})


@app.route('/serv/<serv_id>/tasks', methods=['GET'])  # 客服'解决中'问题列表
@validate_decorator(form.GetTasks())
def serv_tasks(serv_id, data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['question_id']:
        try:
            q_id = ObjectId(data['question_id'])
        except InvalidId:
            return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
        result = db.question.find({'_id': {'$lt': q_id}, 'status': 2, 'serv_id': serv_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.question.find({'status': 2, 'serv_id': serv_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    questions = []
    question_ids = []
    users = {}
    for question in result:
        users[question['user_id']] = {}
        q_id = str(question['_id'])
        question_ids.append(q_id)
        questions.append({
            'question_id': q_id,
            'user_id': question['user_id'],
            'title': question['title'],
            'timestamp': question['timestamp'],
            'status': question['status'],
        })
    for user in db.user.find({'_id': {'$in': [ObjectId(uid) for uid in users.keys()]}}, {'name': 1, 'image_id': 1}):
        users[str(user['_id'])] = {
            'name': user.get('name', u'未填'),
            'image_id': user.get('image_id'),
        }

    last_questions = {}
    for last_question in db.question_message.aggregate([
        {
            '$match': {'question_id': {'$in': question_ids}, 'type': {'$in': [1, 2, 3]}}
        },
        {
            '$sort': {'_id': 1}
        },
        {
            '$group': {
                '_id': '$question_id',
                'timestamp': {'$last': '$timestamp'},
                'sender': {'$last': '$sender'},
                'sender_type': {'$last': '$sender_type'},
                'text': {'$last': '$text'},
                'type': {'$last': '$type'},
            }
        }
    ]):
        last_questions[last_question['_id']] = {
            'timestamp': last_question['timestamp'],
            'sender': last_question['sender'],
            'sender_type': last_question['sender_type'],
            'text': last_question['text'],
            'type': last_question['type'],
        }

    identify = data['identify'] if data['identify'] else 'default'
    for question in questions:
        try:
            user = users[question['user_id']]
            question['user_name'] = user.get('name', u'未填')
            question['user_image_url'] = user_image_normal_path % user['image_id'] if user['image_id'] else \
                user_image_normal_path_default % identify
        except KeyError:
            question['user_name'] = u'未填'
            question['user_image_url'] = user_image_normal_path_default % identify

        try:
            last_question = last_questions[question['question_id']]
            question['last_mess_timestamp'] = last_question['timestamp']
            question['last_mess_sender'] = last_question['sender']
            question['last_mess_sender_type'] = last_question['sender_type']
            if last_question['type'] == 3:
                question['last_mess_text'] = last_question['text']
            elif last_question['type'] == 2:
                question['last_mess_text'] = u'[图片]'
            else:
                question['last_mess_text'] = u'[语音]'
        except:
            question['last_mess_text'] = ''
            question['last_mess_timestamp'] = question['timestamp']
            question['last_mess_sender'] = question['user_id']
            question['last_mess_sender_type'] = 1

    return respond({
        'status': 200,
        'questions': questions,
    })


def get_questions(result):
    questions = []
    for question in result:
        questions.append({
            'question_id': str(question['_id']),
            'user_id': question['user_id'],
            'timestamp': question['timestamp']
        })
    return questions


@app.route('/user/<user_id>/waits', methods=['GET'])  # 用户'待解决'问题列表
@validate_decorator(form.GetTasks())
def user_waits(user_id, data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['question_id']:
        try:
            q_id = ObjectId(data['question_id'])
        except InvalidId:
            return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
        result = db.question.find({'_id': {'$lt': q_id}, 'status': 1, 'user_id': user_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.question.find({'status': 1, 'user_id': user_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    return respond({
        'status': 200,
        'questions': get_questions(result),
    })


@app.route('/user/<user_id>/tasks', methods=['GET'])  # 用户'解决中'问题列表
@validate_decorator(form.GetTasks())
def user_tasks(user_id, data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['question_id']:
        try:
            q_id = ObjectId(data['question_id'])
        except InvalidId:
            return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
        result = db.question.find({'_id': {'$lt': q_id}, 'status': 2, 'user_id': user_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.question.find({'status': 2, 'user_id': user_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    return respond({
        'status': 200,
        'questions': get_questions(result),
    })


@app.route('/user/<user_id>/overs', methods=['GET'])  # 用户'已解决'问题列表
@validate_decorator(form.GetTasks())
def user_overs(user_id, data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['question_id']:
        try:
            q_id = ObjectId(data['question_id'])
        except InvalidId:
            return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
        result = db.question.find({'_id': {'$lt': q_id}, 'status': 3, 'user_id': user_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.question.find({'status': 3, 'user_id': user_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    return respond({
        'status': 200,
        'questions': get_questions(result),
    })


@app.route('/user/<user_id>/alls', methods=['GET'])  # 用户所有问题列表
@validate_decorator(form.GetTasks())
def user_alls(user_id, data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['question_id']:
        try:
            q_id = ObjectId(data['question_id'])
        except InvalidId:
            return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
        result = db.question.find({'_id': {'$lt': q_id}, 'user_id': user_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.question.find({'user_id': user_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    return respond({
        'status': 200,
        'questions': get_questions(result),
    })


@app.route('/question/<question_id>/message', methods=['GET'])  # 获取问题聊天消息
@validate_decorator(form.GetMessages())
def question_message(question_id, data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['message_id']:
        try:
            m_id = ObjectId(data['message_id'])
        except InvalidId:
            return respond({'status': 300, 'error': E_params, 'field': 'message_id', 'debug': 'unregular ObjectId'})
        result = db.question_message.find({'_id': {'$lt': m_id}, 'question_id': question_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.question_message.find({'question_id': question_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    message_list = []
    for message in result:
        if message['type'] == 1:
            message['message_id'] = str(message['_id'])
            message['audio_url'] = Q_message_audio_path % message['audio_id']
            del message['_id']
            del message['audio_id']
            message_list.append(message)
        elif message['type'] == 2:
            message['message_id'] = str(message['_id'])
            message['image_url'] = Q_message_image_normal_path % message['image_id']
            del message['_id']
            del message['image_id']
            message_list.append(message)
        else:
            message['message_id'] = str(message['_id'])
            del message['_id']
            message_list.append(message)
    return respond({
        'status': 200,
        'messages': message_list,
    })


@app.route('/question/<question_id>/message/send_text', methods=['POST'])  # 发送问题聊天文字消息
@validate_decorator(form.TextMessage())
def question_message_send_text(question_id, data):
    try:
        q_id = ObjectId(question_id)
    except InvalidId:
        return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
    question = db.question.find_one({'_id': q_id}, {'status': 1, 'user_id': 1, 'serv_id': 1})
    if not question:
        return respond({'status': 300, 'error': E_quest_nofind})
    status = question.get('status')
    if status == 3:
        return respond({'status': 300, 'error': E_quest_finish, 'debug': 'question alreay finish'})

    timestamp = time()
    message = {
        'question_id': question_id,
        'sender': data['sender'],
        'sender_type': data['sender_type'],
        'timestamp': timestamp,
        'type': 3,
        'text': data['text'],
    }
    mid = str(db.question_message.insert_one(message).inserted_id)
    if data['sender_type'] == 1:
        if status == 2:
            serv = db.service.find_one({'_id': question['serv_id']}, {'user_id': 1})
            if not serv:
                logger.warning('%s serv_id %s not find' % (question_id, question['serv_id']))
                return respond({'status': 300, 'error': E_serv_nofind, 'debug': 'service maybe deleted'})
            push_user = serv.get('user_id')
        else:
            push_user = None
    else:
        push_user = question['user_id']

    # TODO 推送结构与消息体类似,可以重用message字典
    if push_user:
        push(2, push_user, {
            'push_type': 'service',
            'sender': data['sender'],
            'sender_type': data['sender_type'],
            'question_id': question_id,
            'message_id': mid,
            'timestamp': timestamp,
            'type': 3,
            'text': data['text'],
        })
    return respond({
        'status': 200,
        'message_id': mid
    })


@app.route('/question/<question_id>/message/send_image', methods=['POST'])  # 发送问题聊天图片消息
@validate_decorator(form.ImageMessage())
def question_message_send_image(question_id, data):
    try:
        q_id = ObjectId(question_id)
    except InvalidId:
        return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
    question = db.question.find_one({'_id': q_id}, {'user_id': 1, 'serv_id': 1})
    if not question:
        return respond({'status': 300, 'error': E_quest_nofind})
    status = question.get('status')
    if status == 3:
        return respond({'status': 300, 'error': E_quest_finish, 'debug': 'question alreay finish'})

    timestamp = time()
    image_id = Q_message_image.put(data['image'])
    image_url = Q_message_image_normal_path % image_id
    message = {
        'question_id': question_id,
        'sender': data['sender'],
        'sender_type': data['sender_type'],
        'timestamp': timestamp,
        'type': 2,
        'image_id': image_id,
    }
    mid = str(db.question_message.insert_one(message).inserted_id)
    if data['sender_type'] == 1:
        if status == 2:
            serv = db.service.find_one({'_id': question['serv_id']}, {'user_id': 1})
            if not serv:
                logger.warning('%s serv_id %s not find' % (question_id, question['serv_id']))
                return respond({'status': 300, 'error': E_serv_nofind, 'debug': 'service maybe deleted'})
            push_user = serv.get('user_id')
        else:
            push_user = None
    else:
        push_user = question['user_id']

    if push_user:
        push(2, push_user, {
            'push_type': 'service',
            'sender': data['sender'],
            'sender_type': data['sender_type'],
            'question_id': question_id,
            'message_id': mid,
            'timestamp': timestamp,
            'type': 2,
            'image_url': image_url,
        })
    return respond({
        'status': 200,
        'message_id': mid,
        'image_url': image_url,
    })


@app.route('/answer/templates', methods=['GET'])  # 快速回答模板列表
def answer_template():
    return respond({
        'status': 200,
        'templates': [
            {
                'template_id': template['_id'],
                'title': template['title'],
            }
            for template in db.serv_template.find({}, cursor_type=CursorType.EXHAUST)
            ]
    })


@app.route('/answer/template/<template_id>', methods=['GET'])  # 快速回答列表
@validate_decorator(form.GetItems())
def answer_template_item(template_id, data):
    sort = -1 if data['sort'] <= 0 else 1
    if data['item_id']:
        try:
            i_id = ObjectId(data['item_id'])
        except InvalidId:
            return respond({'status': 300, 'error': E_params, 'field': 'item_id', 'debug': 'unregular ObjectId'})
        result = db.serv_template_item.find({'_id': {'$lt': i_id}, 'template_id': template_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])
    else:
        result = db.serv_template_item.find({'template_id': template_id}) \
            .sort('_id', sort).skip(data['page'] * data['num']).limit(data['num'])

    return respond({
        'status': 200,
        'items': [
            {
                'item_id': str(item['_id']),
                'question': item['question'],
                'content': item['content'],
            }
            for item in result
            ]
    })


@app.route('/question/<question_id>/quit', methods=['POST'])  # 退出回答用户问题
@validate_decorator(form.ServId())
def question_quit(question_id, data):
    try:
        q_id = ObjectId(question_id)
    except InvalidId:
        return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
    question = db.question.find_one({'_id': q_id}, {'status': 1, 'user_id': 1})
    if not question:
        return respond({'status': 300, 'error': E_quest_nofind})
    status = question.get('status')
    if status == 2:
        now = time()
        message_id = db.question_message.insert_one({
            'question_id': question_id,
            'type': 4,
            'action': 2,
            'sender': data['serv_id'],
            'sender_type': 2,
            'timestamp': now,
        }).inserted_id
        push(2, question['user_id'], {
            'push_type': 'service',
            'question_id': question_id,
            'message_id': str(message_id),
            'type': 4,
            'action': 2,
            'sender': data['serv_id'],
            'sender_type': 2,
            'timestamp': now,
        })
        db.question.update_one({'_id': q_id}, {'$set': {'status': 1, 'serv_id': data['serv_id']}})
        return respond({'status': 200})
    elif status == 1:
        return respond({'status': 300, 'error': E_quest_unstart})
    else:
        return respond({'status': 300, 'error': E_quest_finish})


@app.route('/question/<question_id>/finish', methods=['POST'])  # 完成用户问题
@validate_decorator(form.ServId())
def question_finish(question_id, data):
    try:
        q_id = ObjectId(question_id)
    except InvalidId:
        return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
    question = db.question.find_one({'_id': q_id}, {'status': 1, 'user_id': 1})
    if not question:
        return respond({'status': 300, 'error': E_quest_nofind})
    status = question.get('status')
    if status == 2:
        now = time()
        message_id = db.question_message.insert_one({
            'question_id': question_id,
            'type': 4,
            'action': 4,
            'sender': data['serv_id'],
            'sender_type': 2,
            'timestamp': now,
        }).inserted_id
        push(2, question['user_id'], {
            'push_type': 'service',
            'question_id': question_id,
            'message_id': str(message_id),
            'type': 4,
            'action': 4,
            'sender': data['serv_id'],
            'sender_type': 2,
            'timestamp': now,
        })
        db.question.update_one({'_id': q_id}, {'$set': {'status': 3, 'serv_id': data['serv_id']}})
        return respond({'status': 200})
    elif status == 1:
        return respond({'status': 300, 'error': E_quest_unstart})
    else:
        return respond({'status': 300, 'error': E_quest_finish})


@app.route('/serv/unbind', methods=['POST'])  # 客服登陆(绑定APP)
@validate_decorator(form.ServBind())
def serv_unbind(data):
    service = db.service.find_one({'_id': data['serv_id']}, {'password': 1})
    if not service:
        return respond({'status': 300, 'error': E_serv_nofind})
    if data['password'] != service['password']:
        return respond({'status': 300, 'error': E_bad_serv_passwd})
    db.service.update_one({'_id': data['serv_id']}, {'$unset': {'user_id': 1}})
    return respond({'status': 200})


@app.route('/user', methods=['GET'])
@validate_decorator(form.QuestionId())
def user(data):
    try:
        q_id = ObjectId(data['question_id'])
    except InvalidId:
        return respond({'status': 300, 'error': E_params, 'field': 'question_id', 'debug': 'unregular ObjectId'})
    question = db.question.find_one({'_id': q_id})
    if not question:
        return respond({'status': 300, 'error': E_quest_nofind})

    try:
        u_id = ObjectId(question['user_id'])
    except InvalidId:
        return respond({'status': 300, 'error': E_params, 'field': 'user_id', 'debug': 'unregular ObjectId'})
    user = db.user.find_one({'_id': u_id})
    if not question:
        return respond({'status': 300, 'error': E_user_nofind})

    try:
        user = {'name': user['name'], 'devices': 1, 'groups': 1}
        return render_template('user.html', user=user)
    except TemplateNotFound:
        abort(404)
