# -*- coding: utf-8 -*-
from flask import Blueprint, request, session, render_template, abort, make_response, jsonify
from functools import wraps, partial
from bson.objectid import ObjectId, InvalidId
from bson.binary import Binary
from pymongo.helpers import DuplicateKeyError
from binascii import b2a_hex
from hashlib import md5
import datetime
import decimal
import types
import json
import conf

from core.db import db
from agent.client import Demand
from agent.alphabet import OK, TIMEOUT

app = Blueprint('admin', __name__, url_prefix='/admin', static_folder='static')
agent = Demand(conf.agent['host'], conf.agent['request_port'])

salt = conf.admin['salt']

def create_admin(username, password, permissions):
    if not isinstance(permissions, (list, tuple)):
        raise ValueError('permissions must iterable')
    nowtime = datetime.datetime.now()
    db.admin.insert_one({
        '_id': username,
        'nickname': username,
        'password': md5(password + salt).hexdigest(),
        'permissions': permissions,
        'maketime': nowtime,
        'lasttime': nowtime
    })


if not db.admin.find_one({'_id': 'admin'}):
    create_admin('admin', 'admin', ['admin'])


def validate_permission(*permissions):
    """
    验证用户session中 permissions 参数中的权限是否符合设置的 permissions
    permissions 中:
        'all' 允许所有权限通过
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_permissions = request.permissions
            if user_permissions:
                for p in permissions:
                    if p == 'all' or p in user_permissions or 'admin' in user_permissions:
                        return func(*args, **kwargs)
            return abort(403)

        return wrapper

    return decorator


menubar = list(db.menubar.find())


@app.route('/', methods=['GET', 'PUT'])
@validate_permission('all')
def inedx():
    user_permissions = request.permissions
    if request.method == 'GET':
        user_menubar = []
        for m in menubar:
            if 'admin' in user_permissions or (set(m['permissions']) & set(user_permissions)):
                user_sub_m = m['submenubar'].copy()
                for sub_m_id, sub_m in m['submenubar'].items():
                    if 'admin' in user_permissions or (set(sub_m['permissions']) & set(user_permissions)):
                        continue
                    else:
                        del user_sub_m[sub_m_id]
                m['submenubar'] = user_sub_m
                user_menubar.append(m)
        return render_template('admin.html', menubar=user_menubar, username=session['nickname'])
    elif request.method == 'PUT':
        if request.data == 'permissions':
            return json.dumps(user_permissions)
    else:
        return abort(405)


def bson_binary_convert(obj):
    if hasattr(obj, 'iteritems'):
        return {k: bson_binary_convert(v) for k, v in obj.iteritems()}
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, unicode)):
        return list((bson_binary_convert(v) for v in obj))
    return b2a_hex(obj) if isinstance(obj, Binary) else obj


def custom_dumps_fix(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime.datetime):
        if obj.year < 1900:
            return '00-00-00 00:00:00'
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(obj, datetime.date):
        if obj.year < 1900:
            return '00-00-00'
        return obj.strftime('%Y-%m-%d')
    if isinstance(obj, datetime.time):
        return obj.strftime('%H:%M')
    if isinstance(obj, decimal.Decimal):
        return "%.2f" % obj
    raise TypeError(repr(obj) + ' is not JSON serializable')


dumps = partial(json.dumps, default=custom_dumps_fix)


def year_to_datetime(year):
    return datetime.datetime(int(year), 1, 1)


def hour_to_datetime(hour):
    return datetime.datetime(1970, 1, 1, int(hour))


def str_to_ObjectId(str24):
    return ObjectId(str24)


types.YearType = year_to_datetime
types.HourType = hour_to_datetime
types.ObjectIdType = str_to_ObjectId


def custom_loads_fix(obj):
    if '__type__' in obj:
        obj_type = getattr(types, obj['__type__'], None)
        if obj_type:
            return obj_type(obj['__value__'])
    return obj


loads = partial(json.loads, object_hook=custom_loads_fix)


def parse_request_params(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if request.mimetype == 'application/json':
            request_params = loads(request.data)
        elif request.form:
            p = {}
            for k, v in request.form.items():
                if v:
                    p[k] = loads(v)
            request_params = p
        elif request.args:
            p = {}
            for k, v in request.args.items():
                if v:
                    p[k] = loads(v)
            request_params = p
        elif request.data:
            request_params = loads(request.data)
        else:
            request_params = {}
        request.params = request_params
        return func(*args, **kwargs)

    return decorator


@app.route('/<collection>', methods=['GET', 'POST'])
@validate_permission('all')
@parse_request_params
def collection_handle(collection):
    if request.method == 'GET':
        page = int(request.params.get('page', 0))
        num = int(request.params.get('num', 10))
        num = num if num <= 1000 else 1000
        find = request.params.get('find', {})
        fields = {f: 1 for f in request.params.get('field', [])}
        sort = request.params.get('sort', ('_id', -1))
        if fields:
            datas = list(db[collection].find(find, fields).sort(*sort).limit(num).skip(page * num))
        else:
            datas = list(db[collection].find(find).sort(*sort).limit(num).skip(page * num))
        return dumps(datas)
    elif request.method == 'POST':
        ok = 0
        if collection == 'appstore.category' and 'category_manage' in request.permissions:
            ok = 1
        elif 'admin' in request.permissions:
            ok = 1
        if ok == 1:
            db[collection].update_many(request.params['find'], request.params['update'])
        return 'success'


@app.route('/<collection>/<handle>', methods=['GET'])
@validate_permission('all')
def collection_handleing(collection, handle):
    if handle == 'count':
        return str(db[collection].find(loads(request.args.get('find', '{}'))).count())
    elif handle == 'aggregate':
        return dumps(list(db[collection].aggregate(loads(request.args['pipeline']))))
    else:
        return abort(403)


@app.route('/watch/getlist', methods=['GET'])
def watch_getlist():
    imei = request.args.get('imei')
    if imei:
        if agent.find(imei) == OK:
            return '["%s"]' % imei
        else:
            return '[]'
    else:
        imei_list = agent.getlist(request.args.get('page', 0), request.args.get('num', 10))
        return dumps(imei_list)


@app.route('/watch/gettotal', methods=['GET'])
def watch_gettotal():
    return str(agent.gettotal())


@app.route('/watch/instruct', methods=['POST'])
@parse_request_params
def watch_instruct():
    imei = request.params.get('imei')
    if not imei:
        return dumps({'status': 400, 'result': 'not imei exists'})
    data = str(request.params.get('instruct', ''))
    if not data:
        return dumps({'status': 400, 'result': 'not data exists'})
    result = agent.send_nowait(imei, data)
    if result == OK:
        return dumps({'status': 200, 'result': result})
    else:
        return dumps({'status': 300, 'result': result})


@app.route('/profile', methods=['GET', 'POST'])
@validate_permission('all')
@parse_request_params
def profile():
    username = session.get('username')
    if request.method == 'GET':
        user = db.admin.find_one({'_id': username}, {'password': 0})
        if not user:
            session.clear()
            return abort(403)
        return dumps(user)
    else:
        for limit in ('permissions', 'lasttime', 'maketime', '_id'):
            if limit in request.params:
                return abort(403)
        result = db.admin.update_one({'_id': username}, {'$set': request.params})
        if result.matched_count:
            if 'nickname' in request.params:
                session['nickname'] = request.params['nickname']
            return 'success'
        else:
            session.clear()
            return abort(403)


@app.route('/admin', methods=['GET', 'POST'])
@parse_request_params
def admin():
    if request.method == 'GET':
        page = int(request.params.get('page', 0))
        num = int(request.params.get('num', 10))
        num = num if num <= 1000 else 1000
        find = request.params['find']
        fields = {f: 1 for f in request.params.get('field', [])}
        if 'sort' in request.params:
            sort = request.params['sort']
        else:
            sort = ('_id', -1)
        datas = list(db.admin.find(find, fields).sort(*sort).limit(num).skip(page * num))
        return dumps(datas)
    else:
        if 'admin' not in request.permissions:
            return abort(403)
        uid = request.params.get('_id')
        if not uid:
            return 'not _id exists'
        update = {}
        if request.params.get('nickname'):
            update['password'] = md5(request.params['nickname'] + salt).hexdigest()
        if request.params.get('permissions') and uid != 'admin':
            update['permissions'] = request.params['permissions']
        result = db.admin.update_one({'_id': uid}, {'$set': update})
        if result.matched_count:
            return 'success'
        else:
            return repr(result)


@app.route('/admin/create', methods=['POST'])
@validate_permission('admin')
@parse_request_params
def admin_create():
    uid = request.params.get('_id')
    if not uid:
        return 'not _id exists'
    nickname = request.params['nickname'] if request.params.get('nickname') else uid
    permissions = request.params.get('permissions')
    if not permissions:
        return 'permissions not exists'
    try:
        create_admin(uid, nickname, permissions)
    except DuplicateKeyError:
        return 'admin already exists'
    return 'success'


@app.route('/admin/delete', methods=['POST'])
@validate_permission('admin')
@parse_request_params
def admin_delete():
    uid = request.params.get('_id')
    if not uid:
        return 'not _id exists'
    db.admin.delete_one({'_id': uid})
    return 'success'
